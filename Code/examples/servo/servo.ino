/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/
#include <ESP32Servo.h>
#define beepOn 0
#define beepOff 1
char beepPin = 9;

int aServoAngle = 90;
int bServoAngle = 120;
int cServoAngle = 120;
int dServoAngle = 90;

Servo Aservo;  // create servo object to control a servo, servo1
Servo Bservo;  //servo2
Servo Cservo;  //servo3
Servo Dservo;  //servo4

// Possible PWM GPIO pins on the ESP32-C3: 0(used by on-board button),1-7,8(used by on-board LED),9-10,18-21
char AservoPin = 4;  // GPIO pin used to connect the servo control (digital out)
char BservoPin = 5;
char CservoPin = 6;
char DservoPin = 7;

// time of servo
int servoDelayTime = 15;

void setup() {
  Serial.begin(115200);

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

  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);
  delay(2000);
}

void loop() {
  for(char i=0; i<180; i++){
    Cservo.write(i);
    delay(servoDelayTime);
  }
  for(char i=180; i>0; i--){
    Cservo.write(i);
    delay(servoDelayTime);
  }
}


