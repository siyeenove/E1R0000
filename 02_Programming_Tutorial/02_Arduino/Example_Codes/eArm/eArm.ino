/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/
#include <WiFi.h>
#include <ESP32Servo.h>
//#include <Ticker.h>
#include "src/eArm.h"
#include "src/app_server.h"

eArm arm;
int xL,yL,xR,yR;
unsigned long t_claw = 0;

// Define Network SSID & Password
// Set ap to 1 to use mCar as Standalone Access Point with default IP 192.168.4.1
// Set ap to 0 to connect to a router using DHCP with hostname espressif
bool ap = 1;
const char* ssid = "eArm";  //AP Name or Router SSID
const char* password = "";  //Password. Leave blank for open network.

// AP Settings
int channel = 11;       // Channel for AP Mode
int hidden = 0;         // Probably leave at zero
int maxconnection = 1;  // Only one device is allowed to connect

//Ticker Timer1;
//unsigned int DservoTicks = 0;

// Right joystick
char beepPin = 9;
#define beepOn 0
#define beepOff 1
#define beepFreq 1000
#define beepDelayTime 1000000 / beepFreq

// 0: joystick, 1: web app
char ControlMode = 0;

// Create one task handle and initialize it.
TaskHandle_t TASK_HandleOne = NULL;

///////////////////////////////////////////////////////////////
void turn_lr(void){
  if(yL<=1500 || 2595<yL){
    if(0<=yL && yL<=300)   {arm.right(5);return;}
    if(3795<yL && yL<=4095){arm.left(5);return;}  
    if(300<yL && yL<=600)  {arm.right(10);return;}
    if(3495<yL && yL<=3795){arm.left(10);return;}
    if(600<yL && yL<=900)  {arm.right(15);return;}
    if(3195<yL && yL<=3495){arm.left(15);return;}
    if(900<yL && yL<=1200) {arm.right(20);return;}
    if(2895<yL && yL<=3195){arm.left(20);return;}
    if(1200<yL && yL<=1500){arm.right(25);return;}
    if(2595<yL && yL<=2895){arm.left(25);return;}
  }
}
///////////////////////////////////////////////////////////////
// Upper Arm
void turn_ua_ud(void){
  if(xL<=1500 || 2595<xL){
    if(0<=xL && xL<=300)   {arm.ua_down(10);return;}
    if(3795<xL && xL<=4095){arm.ua_up(10);return;} 
    if(300<xL && xL<=600)  {arm.ua_up(20);return;}
    if(3495<xL && xL<=3795){arm.ua_down(20);return;}
    if(600<xL && xL<=900)  {arm.ua_up(25);return;}
    if(3195<xL && xL<=3495){arm.ua_down(25);return;}
    if(900<xL && xL<=1200) {arm.ua_up(30);return;}
    if(2895<xL && xL<=3195){arm.ua_down(30);return;}
    if(1200<xL && xL<=1500){arm.ua_up(35);return;}
    if(2595<xL && xL<=2895){arm.ua_down(35);return;} 
  }
}
///////////////////////////////////////////////////////////////
// Forearm
void turn_fa_ud(void){
  if(xR<=1500 || 2595<xR){
    if(0<=xR && xR<=300)   {arm.fa_down(10);return;}
    if(3795<xR && xR<=4095){arm.fa_up(10);return;} 
    if(300<xR && xR<=600)  {arm.fa_up(20);return;}
    if(3495<xR && xR<=3795){arm.fa_down(20);return;}
    if(600<xR && xR<=900)  {arm.fa_up(25);return;}
    if(3195<xR && xR<=3495){arm.fa_down(25);return;}
    if(900<xR && xR<=1200) {arm.fa_up(30);return;}
    if(2895<xR && xR<=3195){arm.fa_down(30);return;}
    if(1200<xR && xR<=1500){arm.fa_up(35);return;}
    if(2595<xR && xR<=2895){arm.fa_down(35);return;} 
  }
}
///////////////////////////////////////////////////////////////
void claw(void){
  if(yR<=1500 || 2595<yR){
    t_claw = millis();

    if(0<=yR && yR<=300)   {arm.clawClose(5);return;}
    if(3795<yR && yR<=4095){arm.clawOpen(5);return;} 
    if(300<yR && yR<=600)  {arm.clawClose(5);return;}
    if(3495<yR && yR<=3795){arm.clawOpen(5);return;}
    if(600<yR && yR<=900)  {arm.clawClose(10);return;}
    if(3195<yR && yR<=3495){arm.clawOpen(10);return;}
    if(900<yR && yR<=1200) {arm.clawClose(15);return;}
    if(2895<yR && yR<=3195){arm.clawOpen(15);return;}
    if(1200<yR && yR<=1500){arm.clawClose(20);return;}
    if(2595<yR && yR<=2895){arm.clawOpen(20);return;} 
  }

  if(millis() - t_claw > 45000){
    // Prevent the servo of the claws from overheating.
    arm.clawRelease();
  }
}
///////////////////////////////////////////////////////////////
void date_processing(int *x,int *y){
  if(abs(2048-*x)>abs(2048-*y))
    {*y = 2048;}
  else
    {*x = 2048;}
}
///////////////////////////////////////////////////////////////
// The function body of task, since the input parameter is NULL,
// so the function body needs to be void * parameter, otherwise an error is reported.
void TASK_ONE(void* param) {
  for (;;) {
    //Select control mode
    if (!arm.JoyStickR.read_z()) {
      delay(5);                                       // Eliminate key jitter.
      if (!arm.JoyStickR.read_z()) {                  // The key is pressed.
        delay(20);
        ControlMode = 1 - ControlMode;
        if (ControlMode == 0) {
          Serial.println("Joystick Control.");
          for(int i=0; i<600; i++){
            digitalWrite(beepPin, beepOn);
            delayMicroseconds(200);
            digitalWrite(beepPin, beepOff);
            delayMicroseconds(300);
          }
        } else {
          Serial.println("Web app Control.");
          for(char i=0; i<100; i++){
            digitalWrite(beepPin, beepOn);
            delayMicroseconds(200);
            digitalWrite(beepPin, beepOff);
            delayMicroseconds(300);
          }
        }
        while (!arm.JoyStickR.read_z());  // The key is released.
      }
    }

    // beep
    while (!arm.JoyStickL.read_z() || App.beepkey == 1) {
      digitalWrite(beepPin, beepOn);
      delayMicroseconds(beepDelayTime);
      digitalWrite(beepPin, beepOff);
      delayMicroseconds(beepDelayTime);
    }
  }
}
///////////////////////////////////////////////////////////////
/*
void callback1() {
  // Prevent the servo of the claws from overheating.
  if(DservoTicks < 500){
    DservoTicks++;
  }
  arm.clawRelease();
}
*/
///////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(115200);

  // For wifi
  Serial.println("ssid: " + (String)ssid);
  Serial.println("password: " + (String)password);
  if (!ap) {
    // Connect to Router
    Serial.println("WiFi is Client mCar!");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.print("mCar Ready! Use 'http://");
    Serial.print(WiFi.localIP());
    Serial.println("' to connect");
  } else {
    // Setup Access Point
    Serial.println("WiFi is Standalone mCar!");
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password, channel, hidden, maxconnection);
    Serial.print("mCar Ready! Use 'http://");
    Serial.print(WiFi.softAPIP());
    Serial.println("' to connect");
  }

  // Webserver / Controls Function
  startCarServer();
  delay(1000);
  displayWindow("P: 100%");

  //arm of servo motor connection pins
  arm.ServoAttach(4,5,6,7);

  //arm of joy stick connection pins : xL,yL,zL,xR,yR,zR
  arm.JoyStickAttach(0,1,10,2,3,8);

  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);

  //Define the thread
  xTaskCreate(
    TASK_ONE,   // Task function
    "TaskOne",  // Task name
    32 * 1024,  // Stack size, set as needed
    NULL,
    1,               // priority
    &TASK_HandleOne  // Task handle
  );

  // Periodic trigger
  // The timing time should be greater than 20ms.
  //Timer1.attach_ms(80, callback1);  // Execute callback1 every 80 milliseconds
}
///////////////////////////////////////////////////////////////
void loop() {
  //Joystick Control
  if (ControlMode == 0) {
    xL = arm.JoyStickL.read_x();
    yL = arm.JoyStickL.read_y();
    xR = arm.JoyStickR.read_x();
    yR = arm.JoyStickR.read_y();
    date_processing(&xL,&yL);
    date_processing(&xR,&yR);
  }
  //Web app Control
  else if (ControlMode == 1) {
    xL = 2048;
    yL = 2048;
    xR = 2048;
    yR = 2048;

    if (App.aAddKey == 1) {   //Serial.println("A+ key is pressed!");
      yL = 3950;
    }

    if (App.aMinKey == 1) {   //Serial.println("A- key is pressed!");
      yL = 150;
    }

    if (App.bAddKey == 1) {  //Serial.println("B+ key is pressed!");
      xL = 150;
    }

    if (App.bMinKey == 1) {  //Serial.println("B- key is pressed!");
      xL = 3950;
    }

    if (App.cAddKey == 1) {  //Serial.println("C+ key is pressed!");
      xR = 150;
    }

    if (App.cMinKey == 1) {  //Serial.println("C- key is pressed!");
      xR = 3950;
    }

    if (App.dAddKey == 1) {  //Serial.println("D+ key is pressed!");
      yR = 3350;
    }

    if (App.dMinKey == 1) {  //Serial.println("D- key is pressed!");
      yR = 750;
    }
  }
  turn_lr();
  turn_ua_ud();
  turn_fa_ud();
  claw();
}
