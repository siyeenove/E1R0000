/*
 * This code applies to siyeenove mechanical arm
 * Through this link you can download the source code:
 * https://github.com/siyeenove
 * Company web site:
 * https://siyeenove.com/
 *                                     ________
 *                         ----|D_servo| 
 *                        |            --------
 *                    |C_servo|   
 *                        |
 *                        |
 *                    |B_servo|
 *                        |
 *                        |
 *                  ___________
 *                  | A_servo |
 *         ____________________
 *         ____________________
 * Fanctions:
 * arm.A_servo.read();   //read the servo of angle
 * arm.B_servo.read();
 * arm.C_servo.read();
 * arm.D_servo.read();
 * 
 * arm.A_servo.write(angle);   //servo run
 * arm.B_servo.write(angle);
 * arm.C_servo.write(angle);
 * arm.D_servo.write(angle);
 * 
 * arm.left(speed);     //execution the action 
 * arm.right(speed);
 * arm.ua_up(speed);    //Upper Arm
 * arm.ua_down(speed);  //Upper Arm
 * arm.fa_up(speed);    //Forearm
 * arm.fa_down(speed);  //Forearm
 * arm.clawOpen(speed);
 * arm.clawClose(speed);
 * arm.clawRelease();
 * 
 * arm.recordAction();    //Record the current action,return pointer array
 * arm.executionAction(int *p,int speed);  //P is a pointer to the array
 * 
 * arm.JoyStickL.read_x(); //Returns joystick numerical
 * arm.JoyStickL.read_y();
 * arm.JoyStickR.read_x();
 * arm.JoyStickR.read_y();
 */
#include "src/eArm.h"
#define buzzerPin 9

eArm arm;
int xL,yL,xR,yR;

const int act_max=20;     //Default 20 action,4 the Angle of servo， max=10000
int act[act_max][4];      //Only can change the number of action
int num=0,num_do=0;
unsigned long t_claw = 0;

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
    if(0<=yR && yR<=300)   {arm.clawClose(0);return;}
    if(3795<yR && yR<=4095){arm.clawOpen(0);return;} 
    if(300<yR && yR<=600)  {arm.clawClose(5);return;}
    if(3495<yR && yR<=3795){arm.clawOpen(5);return;}
    if(600<yR && yR<=900)  {arm.clawClose(10);return;}
    if(3195<yR && yR<=3495){arm.clawOpen(10);return;}
    if(900<yR && yR<=1200) {arm.clawClose(15);return;}
    if(2895<yR && yR<=3195){arm.clawOpen(15);return;}
    if(1200<yR && yR<=1500){arm.clawClose(20);return;}
    if(2595<yR && yR<=2895){arm.clawOpen(20);return;} 

    t_claw = millis();
  }

  if(millis() - t_claw > 40000){
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
void buzzer(int H,int L){
  while(!arm.JoyStickL.read_z()){
    digitalWrite(buzzerPin,LOW);
    delayMicroseconds(H);
    digitalWrite(buzzerPin,HIGH);
    delayMicroseconds(L);
  }
  while(!arm.JoyStickR.read_z()){
    digitalWrite(buzzerPin,LOW);
    delayMicroseconds(H);
    digitalWrite(buzzerPin,HIGH);
    delayMicroseconds(L);
  }
}
///////////////////////////////////////////////////////////////
void Re_action(void){
  if(!arm.JoyStickL.read_z()){
    buzzer(600,400);

    int *p;
    p=arm.recordAction();
    for(char i=0;i<4;i++){
      act[num][i]=*p;
      p=p+1;     
    }
    num++;
    num_do=num;
    if(num>=act_max){
      num=act_max;
      for(int i=0;i<2000;i++){
        digitalWrite(buzzerPin,LOW);
        delayMicroseconds(600);
        digitalWrite(buzzerPin,HIGH);
        delayMicroseconds(400);        
      }
    }
    while(!arm.JoyStickL.read_z());
    //Serial.println(act[0][0]);
  }
}
///////////////////////////////////////////////////////////////
void Ex_action(void){
  unsigned long button_t = 0;
  if(!arm.JoyStickR.read_z()){
    buzzer(200,300);

    // If no actions are recorded, return.
    if(num_do == 0){
      while(!arm.JoyStickR.read_z());
      delay(500);
      for(int i=0;i<2000;i++){
        digitalWrite(buzzerPin,LOW);
        delayMicroseconds(200);
        digitalWrite(buzzerPin,HIGH);
        delayMicroseconds(300);        
      }
      return;
    }

    while(!arm.JoyStickR.read_z());

    // A loop executes the recorded action.
    while(1){
      for(int i=0;i<num_do;i++){
        // Execution action
        arm.executionAction(act[i],15);

        button_t = millis();
        // Long press the key to exit the loop.
        while(!arm.JoyStickR.read_z()){
          if(millis() - button_t > 2000){
            for(int i=0;i<2000;i++){
              digitalWrite(buzzerPin,LOW);
              delayMicroseconds(200);
              digitalWrite(buzzerPin,HIGH);
              delayMicroseconds(300);        
            }
            while(!arm.JoyStickR.read_z());
            return;
          }
        }
      }
    }
  }
}
///////////////////////////////////////////////////////////////
void setup() {
  //Serial.begin(9600);
  //arm of servo motor connection pins
  arm.ServoAttach(4,5,6,7);

  //arm of joy stick connection pins : xL,yL,xR,yR
  arm.JoyStickAttach(0,1,10,2,3,8);

  pinMode(buzzerPin,OUTPUT);
  digitalWrite(buzzerPin,HIGH);
}
///////////////////////////////////////////////////////////////
void loop() {

  xL = arm.JoyStickL.read_x();
  yL = arm.JoyStickL.read_y();
  xR = arm.JoyStickR.read_x();
  yR = arm.JoyStickR.read_y();
  date_processing(&xL,&yL);
  date_processing(&xR,&yR);
  turn_lr();
  turn_ua_ud();
  turn_fa_ud();
  claw();

  Re_action();   // Record the action
  Ex_action();   // execution the action
}

