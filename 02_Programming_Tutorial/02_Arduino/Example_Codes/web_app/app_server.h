#ifndef _APP_SERVER_H
#define _APP_SERVER_H
/* 
*  Libraries. If you get errors compiling, please downgrade ESP32 by Espressif.
*  Use version 2.0.14 (Tools, Manage Libraries).
*/
#include "Arduino.h"
#include "esp_http_server.h"
#include "index/index.h"

httpd_handle_t app_httpd = NULL;
#define maxDisplayStorage 40
// It is used to store real-time data for the App.
struct eAmrApp{
  // For display window
  char *WindowStr = "0";

  char beepkey = 0;
  char aAddKey = 0;
  char aMinKey = 0;
  char bAddKey = 0;
  char bMinKey = 0;
  char cAddKey = 0;
  char cMinKey = 0;
  char dAddKey = 0;
  char dMinKey = 0;
}App;

// Interrupt 
static esp_err_t cmd_handler(httpd_req_t *req){
    char*  buf;
    size_t buf_len;
    char variable[32] = {0,};
    char value[32] = {0,};

    buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1) {
      buf = (char*)malloc(buf_len);
      if(!buf){
        httpd_resp_send_500(req);
        return ESP_FAIL;
      }
      if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
        if (httpd_query_key_value(buf, "var", variable, sizeof(variable)) != ESP_OK ||
          httpd_query_key_value(buf, "val", value, sizeof(value)) != ESP_OK) {
          free(buf);
          httpd_resp_send_404(req);
          return ESP_FAIL;
        }
      } else {
        free(buf);
        httpd_resp_send_404(req);
        return ESP_FAIL;
      }
      free(buf);
    } else {
      httpd_resp_send_404(req);
      return ESP_FAIL;
    }

    int val = atoi(value);
    int res = 0;
    //App Control
    if(!strcmp(variable, "arm")){ 
      //Serial.println(val); 
      if (val & (1<<0)){                  
        App.beepkey = 1;
      }else {
        App.beepkey = 0;
      }

      if (val & (1<<1)){            
        App.aAddKey = 1; 
      }else{
        App.aAddKey = 0; 
      } 

      if (val & (1<<2)){           
        App.aMinKey = 1; 
      }else{
        App.aMinKey = 0;
      } 
      
      if (val & (1<<3)){            
        App.bAddKey = 1;   
      }else{
        App.bAddKey = 0; 
      } 
      
      if (val & (1<<4)){           
        App.bMinKey = 1; 
      }else{
        App.bMinKey = 0; 
      }
      
      if (val & (1<<5)){            
        App.cAddKey = 1;   
      }else{
        App.cAddKey = 0;
      } 
      
      if (val & (1<<6)){           
        App.cMinKey = 1; 
      }else{
        App.cMinKey = 0; 
      } 
      
      if (val & (1<<7)){            
        App.dAddKey = 1;   
      }else{
        App.dAddKey = 0;
      } 
      
      if (val & (1<<8)){           
        App.dMinKey = 1;  
      }else{                       
        App.dMinKey = 0;
      } 
    }else{ 
      //Serial.println("variable");
      res = -1; 
    }

  if(res){ return httpd_resp_send_500(req); }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

// window: 0=left window, 1=right window, 2=voltage window; str: strlen(str)<=40
void displayWindow(char *str){   
  if(strlen(str)>maxDisplayStorage){
    return;
  }
  App.WindowStr = str;
}

static esp_err_t display_handler(httpd_req_t *req){
  // windowResponse[0] is used to distinguish between left and right display Windows of the web app.
  char windowResponse[maxDisplayStorage + 1] = {};    

  windowResponse[0] = 'A'; 
  sprintf(&windowResponse[1], "%s", App.WindowStr);

  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, windowResponse, strlen(windowResponse));
}

static esp_err_t index_handler(httpd_req_t *req){
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, (const char *)INDEX_HTML, strlen(INDEX_HTML));
}

// Finally, if all is well with the camera, encoding, and all else, here it is, the actual camera server.
// If it works, use your new camera robot to grab a beer from the fridge using function Request.Fridge("beer","buschlite")
void startCarServer(void){
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();

  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t cmd_uri = {
    .uri       = "/control",
    .method    = HTTP_GET,
    .handler   = cmd_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t display_uri = {
    .uri       = "/display",
    .method    = HTTP_GET,
    .handler   = display_handler,
    .user_ctx  = NULL
  };

  Serial.printf("Starting web server on port: '%d'\n", config.server_port);
  if (httpd_start(&app_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(app_httpd, &index_uri);
    httpd_register_uri_handler(app_httpd, &cmd_uri);
    httpd_register_uri_handler(app_httpd, &display_uri);
  }
}

#endif

