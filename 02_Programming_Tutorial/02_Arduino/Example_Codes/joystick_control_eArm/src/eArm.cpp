#include"eArm.h"

eArm::eArm(){}
/////////////////////////////////////////////////////////
void eArm::JoyStickAttach(uint8_t xpin1,uint8_t ypin1,uint8_t xpin2,uint8_t ypin2)
{
  JoyStickL.attach(xpin1,ypin1);
  JoyStickR.attach(xpin2,ypin2);
} 
/////////////////////////////////////////////////////////
void eArm::JoyStickAttach(uint8_t xpin1,uint8_t ypin1,uint8_t zpin1,uint8_t xpin2,uint8_t ypin2,uint8_t zpin2)
{
  JoyStickL.attach(xpin1,ypin1,zpin1);
  JoyStickR.attach(xpin2,ypin2,zpin2);
} 
/////////////////////////////////////////////////////////
void eArm::ServoAttach(uint8_t A_servoPin,uint8_t B_servoPin,uint8_t C_servoPin,uint8_t D_servoPin)
{
  // Allow allocation of all timers
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  A_servo.setPeriodHertz(50);            // Standard 50hz servo
  A_servo.attach(A_servoPin, 500, 2400);  // attaches the servo on pin 18 to the servo object
                                        // using SG90 servo min/max of 500us and 2400us
                                        // for MG995 large servo, use 1000us and 2000us,
                                        // which are the defaults, so this line could be
                                        // "myservo.attach(servoPin);"
  B_servo.setPeriodHertz(50);
  B_servo.attach(B_servoPin, 500, 2400);
  C_servo.setPeriodHertz(50);
  C_servo.attach(C_servoPin, 500, 2400);
  D_servo.setPeriodHertz(50);
  D_servo.attach(D_servoPin, 500, 2400);
  
  // Initialize the servo Angle
  servoCurrentAngle[0]=90;
  servoCurrentAngle[1]=120;
  servoCurrentAngle[2]=60;
  servoCurrentAngle[3]=90;
  A_servo.write(servoCurrentAngle[0]);
  B_servo.write(servoCurrentAngle[1]);
  C_servo.write(servoCurrentAngle[2]);
  D_servo.write(servoCurrentAngle[3]);
}
/////////////////////////////////////////////////////////
// Upper Arm
void eArm::ua_up(int speed)
{
  servoCurrentAngle[1]=servoCurrentAngle[1]+1;
  if(servoCurrentAngle[1]>=180)
    {servoCurrentAngle[1]= 180;}
  B_servo.write(servoCurrentAngle[1]);
  delay(speed);      
}
/////////////////////////////////////////////////////////
// Upper Arm
void eArm::ua_down(int speed)
{
  servoCurrentAngle[1]=servoCurrentAngle[1]-1;
  if(servoCurrentAngle[1]<=0)
    {servoCurrentAngle[1] = 0;}
  B_servo.write(servoCurrentAngle[1]);
  delay(speed);    
}
/////////////////////////////////////////////////////////
// Forearm
void eArm::fa_up(int speed)
{
  servoCurrentAngle[2]=servoCurrentAngle[2]-1;
  if(servoCurrentAngle[2]<=0)
    {servoCurrentAngle[2]= 0;}
  C_servo.write(servoCurrentAngle[2]);
  delay(speed);      
}
/////////////////////////////////////////////////////////
// Forearm
void eArm::fa_down(int speed)
{
  servoCurrentAngle[2]=servoCurrentAngle[2]+1;
  if(servoCurrentAngle[2]>=180)
    {servoCurrentAngle[2] =180;}
  C_servo.write(servoCurrentAngle[2]);
  delay(speed);    
}
/////////////////////////////////////////////////////////
void eArm::left(int speed)
{
  servoCurrentAngle[0]=servoCurrentAngle[0]+1;
  if(servoCurrentAngle[0]>=180)
    {servoCurrentAngle[0] = 180;}
  A_servo.write(servoCurrentAngle[0]);
  delay(speed);       
}
/////////////////////////////////////////////////////////
void eArm::right(int speed)
{
  servoCurrentAngle[0]=servoCurrentAngle[0]-1;
  if(servoCurrentAngle[0]<=0)
    {servoCurrentAngle[0] =0;}
  A_servo.write(servoCurrentAngle[0]);
  delay(speed);    
}
/////////////////////////////////////////////////////////
void eArm::clawOpen(int speed)
{
  servoCurrentAngle[3]=servoCurrentAngle[3]+1;
  if(servoCurrentAngle[3]>=180)
    {servoCurrentAngle[3] =180;}
  D_servo.write(servoCurrentAngle[3]);
  delay(speed);     
}
/////////////////////////////////////////////////////////
void eArm::clawClose(int speed)
{
  servoCurrentAngle[3]=servoCurrentAngle[3]-1;
  if(servoCurrentAngle[3]<=0)
    {servoCurrentAngle[3] =0;}
  D_servo.write(servoCurrentAngle[3]);
  delay(speed);     
}
/////////////////////////////////////////////////////////
void eArm::clawRelease(void)
{
  D_servo.release();    
}
/////////////////////////////////////////////////////////
int *eArm::recordAction(void)
{
  return servoCurrentAngle;	
}
/////////////////////////////////////////////////////////
void eArm::executionAction(int *angle,int speed)
{
  int targetAngle[4];
  // Copy the target Angle to the list
  for(int i=0;i<4;i++){
	targetAngle[i]= *angle;
	angle++;
  }
	
  bool moving = true;
  while(moving){
	moving = false;
	// Update each servo Angle
	for (int i = 0; i < 4; i++) {
		if (servoCurrentAngle[i] != targetAngle[i]) {
			moving = true;
			// Move one step in the direction of the target
			servoCurrentAngle[i] += (targetAngle[i] > servoCurrentAngle[i]) ? 1 : -1;
		}
	}
	
	// Write in servo
	A_servo.write(servoCurrentAngle[0]);
	B_servo.write(servoCurrentAngle[1]);
	C_servo.write(servoCurrentAngle[2]);
	D_servo.write(servoCurrentAngle[3]);
	delay(speed);
  }
  delay(speed*20);
}


