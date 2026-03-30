#include"JoyStick.h"

JoyStick::JoyStick()
{ }
///////////////////////////////////////////////////////////
void JoyStick::attach(uint8_t x_pin,uint8_t y_pin)
{
  _pinX=x_pin;
  _pinY=y_pin;
}
///////////////////////////////////////////////////////////
void JoyStick::attach(uint8_t x_pin,uint8_t y_pin,uint8_t z_pin)
{
  _pinX=x_pin;
  _pinY=y_pin; 
  _pinZ=z_pin;
  pinMode(_pinZ,INPUT_PULLUP); 
}
///////////////////////////////////////////////////////////
int JoyStick::read_x(void)
{
  for(char i=0;i<8;i++){
    buf[i]=analogRead(_pinX);
    }
  x=Eliminate_jitter();
  return x;
}
///////////////////////////////////////////////////////////
int JoyStick::read_y(void)
{
  for(char i=0;i<8;i++){
    buf[i]=analogRead(_pinY);
    }
  y=Eliminate_jitter();
  return y;
}
///////////////////////////////////////////////////////////
bool JoyStick::read_z(void)
{
  return digitalRead(_pinZ);
}
///////////////////////////////////////////////////////////
int JoyStick::Eliminate_jitter(void)
{
  int sum=0;
  for(char i=2;i<6;i++){
    sum+=buf[i];
  }
  sum=sum/4;
  return sum;
}



