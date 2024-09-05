#include <Servo.h>

bool face_rec = true;
static int motor_Driver_Input1 = PIN_PC0;
static int motor_Driver_Input2 = PIN_PC1;
static int motor_Driver_Enable = PIN_PB3;

static int Servo_pin = PIN_PB2;

int ldrpin=PIN_PC2;
int testLED=PIN_PB4;


int buzzer_pin = PIN_PB5;


int PIR_PIN= PIN_PB6;
Servo Door;

void setup() {
  pinMode(motor_Driver_Input1, OUTPUT);
  pinMode(motor_Driver_Input2, OUTPUT);
  pinMode(motor_Driver_Enable, OUTPUT);
  pinMode(testLED, OUTPUT);
  pinMode(ldrpin,INPUT);
  Door.attach(Servo_pin);

  //OpenDoor();
  //delay(500);
  //OpenDoor();


  digitalWrite(motor_Driver_Input1, HIGH);
  digitalWrite(motor_Driver_Input2, LOW);


   digitalWrite(testLED,HIGH); 


   pinMode(buzzer_pin,OUTPUT);


   pinMode(PIR_PIN, INPUT);
}

void SetFanSpeed(int value) {
  analogWrite(motor_Driver_Enable, value);
}

void OpenDoor() {
  Door.write(90);
  delay(1500);
  Door.write(0);
}

void loop() {

 int sensorState = digitalRead(PIR_PIN);

  if (sensorState == HIGH) {
    digitalWrite(testLED, HIGH);
  } else {
    digitalWrite(testLED, LOW);
  }
}
