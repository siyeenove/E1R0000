/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/
#include <WiFi.h>
#include <ESP32Servo.h>
#include "app_server.h"

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

int aServoAngle = 90;
int bServoAngle = 120;
int cServoAngle = 60;
int dServoAngle = 90;
int Volt = 21;

Servo Aservo;  // create servo object to control a servo, servo1
Servo Bservo;  //servo2
Servo Cservo;  //servo3
Servo Dservo;  //servo4

// Possible PWM GPIO pins on the ESP32-C3: 0(used by on-board button),1-7,8(used by on-board LED),9-10,18-21
char AservoPin = 4;  // GPIO pin used to connect the servo control (digital out)
char BservoPin = 5;
char CservoPin = 6;
char DservoPin = 7;

// Left joystick
char left_joystick_UpDownPin = 0;  // GPIO pin used to connect the servo control (digital out)
char left_joystick_LeftRightPin = 1;
char left_joystick_KeyPin = 8;

// Right joystick
char right_joystick_UpDownPin = 2;  // GPIO pin used to connect the servo control (digital out)
char right_joystick_LeftRightPin = 3;
char right_joystick_KeyPin = 10;

// Right joystick
char beepPin = 9;
#define beepOn 0
#define beepOff 1
#define beepFreq 500
#define beepDelayTime 1000000 / beepFreq

// 0: joystick, 1: web app
char ControlMode = 0;
// The sensitivity of the joystick
int sensitivity = 1600;  //0-2048
// Speed of servo
char servoSpeed = 1;
// time of servo
int servoDelayTime = 5;

// Create one task handle and initialize it.
TaskHandle_t TASK_HandleOne = NULL;

// The function body of task, since the input parameter is NULL,
// so the function body needs to be void * parameter, otherwise an error is reported.
void TASK_ONE(void* param) {
  for (;;) {
    //Select control mode
    if (digitalRead(left_joystick_KeyPin) == LOW) {
      delay(5);                                        // Eliminate key jitter.
      if (digitalRead(left_joystick_KeyPin) == LOW) {  // The key is pressed.
        delay(20);
        ControlMode = 1 - ControlMode;
        if (ControlMode == 0) {
          Serial.println("Joystick Control.");
        } else {
          Serial.println("Web app Control.");
          for(char i=0; i<10; i++){
            digitalWrite(beepPin, beepOn);
            delayMicroseconds(1000);
            digitalWrite(beepPin, beepOff);
            delayMicroseconds(1000);
          }
        }
        while (digitalRead(left_joystick_KeyPin) == LOW);  // The key is released.
      }
    }

    // beep
    if (digitalRead(right_joystick_KeyPin) == LOW || App.beepkey == 1) {
      digitalWrite(beepPin, beepOn);
      delayMicroseconds(beepDelayTime);
      digitalWrite(beepPin, beepOff);
      delayMicroseconds(beepDelayTime);
    }
  }
}


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

  // Allow allocation of all timers
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  Aservo.setPeriodHertz(50);            // Standard 50hz servo
  Aservo.attach(AservoPin, 500, 2400);  // attaches the servo on pin 18 to the servo object
                                        // using SG90 servo min/max of 500us and 2400us
                                        // for MG995 large servo, use 1000us and 2000us,
                                        // which are the defaults, so this line could be
                                        // "myservo.attach(servoPin);"
  Bservo.setPeriodHertz(50);
  Bservo.attach(BservoPin, 500, 2400);
  Cservo.setPeriodHertz(50);
  Cservo.attach(CservoPin, 500, 2400);
  Dservo.setPeriodHertz(50);
  Dservo.attach(DservoPin, 500, 2400);

  Aservo.write(aServoAngle);  // set the servo position according to the scaled value
  Bservo.write(bServoAngle);
  Cservo.write(cServoAngle);
  Dservo.write(dServoAngle);

  //Define the thread
  xTaskCreate(
    TASK_ONE,   // Task function
    "TaskOne",  // Task name
    32 * 1024,  // Stack size, set as needed
    NULL,
    1,               // priority
    &TASK_HandleOne  // Task handle
  );

  pinMode(left_joystick_KeyPin, INPUT);
  pinMode(right_joystick_KeyPin, INPUT_PULLUP);
  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);
}

void loop() {
  //Joystick Control
  if (ControlMode == 0) {
    if (analogRead(left_joystick_LeftRightPin) > (2048 + sensitivity)) {
      aServoAngle = aServoAngle + servoSpeed;
      if (aServoAngle > 180) { aServoAngle = 180; }
      delay(servoDelayTime);
      //Serial.println(analogRead(left_joystick_LeftRightPin));
    }
    if (analogRead(left_joystick_LeftRightPin) < (2048 - sensitivity)) {
      aServoAngle = aServoAngle - servoSpeed;
      if (aServoAngle < 0) { aServoAngle = 0; }
      delay(servoDelayTime);
    }

    if (analogRead(left_joystick_UpDownPin) > (2048 + sensitivity)) {
      bServoAngle = bServoAngle + servoSpeed;
      if (bServoAngle > 180) { bServoAngle = 180; }
      delay(servoDelayTime);
      Serial.println(analogRead(left_joystick_UpDownPin));
    }
    if (analogRead(left_joystick_UpDownPin) < (2048 - sensitivity)) {
      bServoAngle = bServoAngle - servoSpeed;
      if (bServoAngle < 0) { bServoAngle = 0; }
      delay(servoDelayTime);
    }

    if (analogRead(right_joystick_LeftRightPin) > (2048 + sensitivity)) {
      dServoAngle = dServoAngle + servoSpeed;
      if (dServoAngle > 180) { dServoAngle = 180; }
      delay(servoDelayTime);
      //Serial.println(analogRead(right_joystick_LeftRightPin));
    }
    if (analogRead(right_joystick_LeftRightPin) < (2048 - sensitivity)) {
      dServoAngle = dServoAngle - servoSpeed;
      if (dServoAngle < 0) { dServoAngle = 0; }
      delay(servoDelayTime);
    }

    if (analogRead(right_joystick_UpDownPin) > (2048 + sensitivity)) {
      cServoAngle = cServoAngle - servoSpeed;
      if (cServoAngle < 0) { cServoAngle = 0; }
      delay(servoDelayTime);
    }
    if (analogRead(right_joystick_UpDownPin) < (2048 - sensitivity)) {
      cServoAngle = cServoAngle + servoSpeed;
      if (cServoAngle > 180) { cServoAngle = 180; }
      delay(servoDelayTime);
    }
  }
  //Web app Control
  else if (ControlMode == 1) {
    if (App.aAddKey == 1) {
      Serial.println("A+ key is pressed!");
      if (aServoAngle < 180) {
        aServoAngle = aServoAngle + servoSpeed;
        if (aServoAngle > 180) { aServoAngle = 180; }
        delay(servoDelayTime);
      }
    }

    if (App.aMinKey == 1) {
      Serial.println("A- key is pressed!");
      if (aServoAngle > 0) {
        aServoAngle = aServoAngle - servoSpeed;
        if (aServoAngle < 0) { aServoAngle = 0; }
        delay(servoDelayTime);
      }
    }

    if (App.bAddKey == 1) {
      Serial.println("B+ key is pressed!");
      if (bServoAngle > 0) {
        bServoAngle = bServoAngle - servoSpeed;
        if (bServoAngle < 0) { bServoAngle = 0; }
        delay(servoDelayTime);
      }
    }

    if (App.bMinKey == 1) {
      Serial.println("B- key is pressed!");
      if (bServoAngle < 180) {
        bServoAngle = bServoAngle + servoSpeed;
        if (bServoAngle > 180) { bServoAngle = 180; }
        delay(servoDelayTime);
      }
    }

    if (App.cAddKey == 1) {
      Serial.println("C+ key is pressed!");
      if (cServoAngle < 180) {
        cServoAngle = cServoAngle + servoSpeed;
        if (cServoAngle > 180) { cServoAngle = 180; }
        delay(servoDelayTime);
      }
    }

    if (App.cMinKey == 1) {
      Serial.println("C- key is pressed!");
      if (cServoAngle > 0) {
        cServoAngle = cServoAngle - servoSpeed;
        if (cServoAngle < 0) { cServoAngle = 0; }
        delay(servoDelayTime);
      }
    }

    if (App.dAddKey == 1) {
      Serial.println("D+ key is pressed!");
      if (dServoAngle > 0) {
        dServoAngle = dServoAngle - servoSpeed;
        if (dServoAngle < 0) { dServoAngle = 0; }
        delay(servoDelayTime);
      }
    }

    if (App.dMinKey == 1) {
      Serial.println("D- key is pressed!");
      if (dServoAngle < 180) {
        dServoAngle = dServoAngle + servoSpeed;
        if (dServoAngle > 180) { dServoAngle = 180; }
        delay(servoDelayTime);
      }
    }
  }
  Aservo.write(aServoAngle);
  Bservo.write(bServoAngle);
  Cservo.write(cServoAngle);
  Dservo.write(dServoAngle);
}
