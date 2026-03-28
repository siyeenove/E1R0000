/*
 * This code applies to siyeenove mechanical arm
 * Through this link you can download the source code:
 * https://github.com/siyeenove
 * Company web site:
 * http://siyeenove.com/
 */
#ifndef EARM_H_
#define EARM_H_ 
#include"JoyStick.h"
#include <ESP32Servo.h>
#include <Arduino.h>

class eArm
{
 public:
     eArm();
	 void JoyStickAttach(uint8_t xpin1,uint8_t ypin1,uint8_t xpin2,uint8_t ypin2);
	 void JoyStickAttach(uint8_t xpin1,uint8_t ypin1,uint8_t zpin1,uint8_t xpin2,uint8_t ypin2,uint8_t zpin2);
     void ServoAttach(uint8_t A_servoPin,uint8_t B_servoPin,uint8_t C_servoPin,uint8_t D_servoPin);
     void ua_up(int speed);    // Upper Arm
     void ua_down(int speed);  // Upper Arm
     void fa_up(int speed);    // Forearm
     void fa_down(int speed);  // Forearm
     void left(int speed);
     void right(int speed);
     void clawOpen(int speed);
     void clawClose(int speed);
	 void clawRelease(void);
	 int *recordAction(void);
	 void executionAction(int *angle,int speed);
 //private:
     int servoCurrentAngle[4];
     Servo A_servo;
     Servo B_servo;
     Servo C_servo;
     Servo D_servo; 
     JoyStick JoyStickL;
     JoyStick JoyStickR; 	 
};
#endif
