#include <Servo.h>

bool face_rec = true;
const int motor_Driver_Input1 = PIN_PB0;
const int motor_Driver_Input2 = PIN_PB1;
const int motor_Driver_Enable = PIN_PB3;

const int Servo_pin = PIN_PB2;

const int LDR_pin = PIN_PC2;
const int testLED = PIN_PB4;
Servo Door;

int THERMISTORPIN = PIN_PC3, BCOEFFICIENT = 3380;
float THERMISTORNOMINAL = 10000, TEMPERATURENOMINAL = 25, SERIESRESISTOR = 10000;

const int Keypad_pin = PIN_PC0;
bool keyPressed = false;

void setup() {
  Serial.begin(9600);

  pinMode(motor_Driver_Input1, OUTPUT);
  pinMode(motor_Driver_Input2, OUTPUT);
  pinMode(motor_Driver_Enable, OUTPUT);
  pinMode(testLED, OUTPUT);
  pinMode(LDR_pin, INPUT);

  Door.attach(Servo_pin);

  digitalWrite(testLED, LOW);
}

void startFan() {
  digitalWrite(motor_Driver_Input1, HIGH);
  digitalWrite(motor_Driver_Input2, LOW);
}

void SetFanSpeed(int value) {
  analogWrite(motor_Driver_Enable, value);
}

void OpenDoor() {
  Door.write(90);
  delay(1500);
  Door.write(0);
}

int GetTemp() {
  int reading = 0;
  for (int i = 0; i < 5; i++) {
    reading += analogRead(THERMISTORPIN);
    delay(10);
  }
  float ADCaverage = reading / 5.0;  // average of Analog reads (0-1023)

  // convert the Analog reading to the value of NTC Resistance
  float ResistanceNTC = SERIESRESISTOR / (1023 / (ADCaverage)-1);

  float Temperature;  //The Steinhart-Hart equation :1/T = 1/T0 + 1/B *ln(R/R0)

  Temperature = 1.0 / (TEMPERATURENOMINAL + 273.15) + log(ResistanceNTC / THERMISTORNOMINAL) / BCOEFFICIENT;
  Temperature = 1.0 / Temperature;  // invert to get Temp in K
  Temperature -= 273.15;            // change to C
  return Temperature;
}
int getKey() {
  char value = getkeyvalue();

  if (value == 0){
    return 0;
  }
  if (keyPressed == false) {
      Serial.println(value);
  }

  if (value > 1000) {
    keyPressed = false;
  }
}
byte getkeyvalue() {

  int adc = analogRead(Keypad_pin);
  switch (adc) {
    case 0 ... 30:
      return '1';
    case 50 ... 90:
      return '2';
    case 110 ... 160:
      return '3';
    case 180 ... 220:
      return 'A';
    case 230 ... 260:
      return '4';
    case 270 ... 320:
      return '5';
    case 321 ... 350:
      return '6';
    case 351 ... 380:
      return 'B';
    case 381 ... 410:
      return '7';
    case 411 ... 440:
      return '8';
    case 441 ... 465:
      return '9';
    case 470 ... 490:
      return 'C';
    case 491 ... 510:
      return '*';
    case 511 ... 530:
      return '0';
    case 531 ... 550:
      return '#';
    case 551 ... 572:
      return 'D';
    default:
      return 0;
  }
  return 0;
}
void loop() {
  getKey();
}
