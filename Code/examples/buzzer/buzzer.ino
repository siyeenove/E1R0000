/*
* Siyeenove eArm - For ESP32 C3
* Boards Manager: esp32 by Espressif Systems, Version 3.0.2  
* Arduino IDE Version: 2.3.2 
*/

#define beepOn 0
#define beepOff 1
#define beepFreq 500
#define beepDelayTime 1000000 / beepFreq
char beepPin = 9;

void setup() {
  pinMode(beepPin, OUTPUT);
  digitalWrite(beepPin, beepOff);
}

void loop() {
  digitalWrite(beepPin, beepOn);
  delayMicroseconds(beepDelayTime);
  digitalWrite(beepPin, beepOff);
  delayMicroseconds(beepDelayTime);
}
