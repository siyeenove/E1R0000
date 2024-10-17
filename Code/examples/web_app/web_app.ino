/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/
#include <WiFi.h>
#include "app_server.h"

#define beepOn 0
#define beepOff 1
char beepPin = 9;

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


// 0: joystick, 1: web app
char ControlMode = 0;
// The sensitivity of the joystick
int sensitivity = 1000;  //0-2048
// Speed of servo
char servoSpeed = 1;
// time of servo
int servoDelayTime = 10;


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
  
  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);
}

void loop() {
  if (App.beepkey == 1) {
    Serial.println("Beep key is pressed!");
  }

  if (App.aAddKey == 1) {
    Serial.println("A+ key is pressed!");
  }

  if (App.aMinKey == 1) {
    Serial.println("A- key is pressed!");
  }

  if (App.bAddKey == 1) {
    Serial.println("B+ key is pressed!");
  }

  if (App.bMinKey == 1) {
    Serial.println("B- key is pressed!");
  }

  if (App.cAddKey == 1) {
    Serial.println("C+ key is pressed!");
  }

  if (App.cMinKey == 1) {
    Serial.println("C- key is pressed!");
  }

  if (App.dAddKey == 1) {
    Serial.println("D+ key is pressed!");
  }

  if (App.dMinKey == 1) {
    Serial.println("D- key is pressed!");
  }
}
