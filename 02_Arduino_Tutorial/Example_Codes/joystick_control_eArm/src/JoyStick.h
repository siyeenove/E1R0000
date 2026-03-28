/*
 * This code applies to siyeenove mechanical arm
 * Through this link you can download the source code:
 * https://github.com/siyeenove
 * Company web site:
 * http://siyeenove.com/
 */
#ifndef JOYSTICK_H_
#define JOYSTICK_H_ 
#include <Arduino.h>

class JoyStick
{
 public:
     JoyStick();
     void attach(uint8_t x_pin,uint8_t y_pin);
     void attach(uint8_t x_pin,uint8_t y_pin,uint8_t z_pin);
     int read_x(void);
     int read_y(void);
     bool read_z(void);
     int Eliminate_jitter(void);
 private:
     uint8_t _pinX;
     uint8_t _pinY;
     uint8_t _pinZ;
     int x;
     int y;
     bool z;
     int buf[20]={};
};
#endif
