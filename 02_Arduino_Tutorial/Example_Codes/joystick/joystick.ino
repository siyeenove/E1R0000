/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/

#define beepOn 0
#define beepOff 1
char beepPin = 9;

// Left joystick
char left_joystick_UpDownPin = 0;  // GPIO pin used to connect the servo control (digital out)
char left_joystick_LeftRightPin = 1;
char left_joystick_KeyPin = 8;

// Right joystick
char right_joystick_UpDownPin = 2;  // GPIO pin used to connect the servo control (digital out)
char right_joystick_LeftRightPin = 3;
char right_joystick_KeyPin = 10;


void setup() {
  Serial.begin(115200);

  pinMode(left_joystick_KeyPin, INPUT);
  pinMode(right_joystick_KeyPin, INPUT_PULLUP);

  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);
}

void loop() {
  Serial.print("Left_joystick_LeftRight:");
  Serial.println(analogRead(left_joystick_LeftRightPin));

  Serial.print("Left_joystick_UpDown:");
  Serial.println(analogRead(left_joystick_UpDownPin));

  Serial.print("Left_joystick_key:");
  Serial.println(analogRead(left_joystick_KeyPin));

  Serial.print("Right_joystick_LeftRight:");
  Serial.println(analogRead(right_joystick_LeftRightPin));

  Serial.print("Right_joystick_UpDown");
  Serial.println(analogRead(right_joystick_UpDownPin));

  Serial.print("Right_joystick_key:");
  Serial.println(analogRead(right_joystick_KeyPin));
  delay(1000);
}






