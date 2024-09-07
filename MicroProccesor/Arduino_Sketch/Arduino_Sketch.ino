#include <Servo.h>

bool face_rec = true;
bool checkPASS = false;
const int motor_Driver_Input1 = PIN_PB0;
const int motor_Driver_Input2 = PIN_PB1;
const int motor_Driver_Enable = PIN_PB4;

const int Servo_pin = PIN_PB2;

const int LDR_pin = PIN_PC2;
const int testLED = PIN_PB3;
Servo Door;

int THERMISTORPIN = PIN_PC3, BCOEFFICIENT = 3380;
float THERMISTORNOMINAL = 10000, TEMPERATURENOMINAL = 25, SERIESRESISTOR = 10000;

const int Keypad_pin = PIN_PC0;
bool keyPressed = false;

const int RedLED=PIN_PB5;
const int GreenLED=PIN_PB6;
const int BlueLED=PIN_PB7;

const int PIR=PIN_PC4;


const int buzzer=PIN_PD3;

void setup() {
  Serial.begin(9600);

  pinMode(motor_Driver_Input1, OUTPUT);
  pinMode(motor_Driver_Input2, OUTPUT);
  pinMode(motor_Driver_Enable, OUTPUT);
  pinMode(testLED, OUTPUT);
  pinMode(LDR_pin, INPUT);

  Door.attach(Servo_pin);

  digitalWrite(testLED, LOW);

  pinMode(RedLED,OUTPUT);
  pinMode(BlueLED,OUTPUT);
  pinMode(GreenLED,OUTPUT);


  pinMode(PIR,INPUT);


  pinMode(buzzer,OUTPUT);

  delay(5000);
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
void lightGreen()
{
digitalWrite(GreenLED,HIGH);
digitalWrite(RedLED,LOW);
digitalWrite(BlueLED,LOW);
}
void lightBlue()
{
digitalWrite(GreenLED,LOW);
digitalWrite(RedLED,LOW);
digitalWrite(BlueLED,HIGH);
}
void lightRed(){
 digitalWrite(GreenLED,LOW);
digitalWrite(RedLED,HIGH);
digitalWrite(BlueLED,LOW); 
}
void detectMotion() {
 while (digitalRead(PIR)==1) {
    Serial.println("Motion detected: Someone is inside.");
    analogWrite(testLED, 255);
    delay(200);
    analogWrite(testLED, 0);
    delay(200);
  }
}

void beebBuzzer(){
  digitalWrite(buzzer,HIGH);
  delay(500);
  digitalWrite(buzzer,LOW);
}

void controlFanSpeed(float temperature) {
  int speed;
  if (temperature > 30) {
    speed = 255;  // Max speed
  } else if (temperature > 20) {
    speed = map(temperature, 20, 30, 128, 255);
  } else {
    speed = 128;
  }
  startFan();
  SetFanSpeed(speed);
}
void displayTempOnRGB(float temperature) {
  if (temperature > 30) {
    lightRed();
  } else if (temperature > 20 && temperature <= 30) {
    lightGreen();
  } else {
    lightBlue();
  }
}
void controlLight(int lightLevel) {
  int brightness = map(lightLevel, 0, 1023, 255, 0); 
  analogWrite(testLED, brightness);
}
void loop() {
  detectMotion();
   char pass[5]; 
  Serial.println("\nEnter Password:");
  for (int i = 0; i < 4; i++) {
    pass[i]=getkeyvalue();
    while (pass[i] == 0) { 
      pass[i] = getkeyvalue();
    }
    Serial.print(pass[i]);  
    delay(300);        
  }

  pass[4] = '\0'; 

  if (strcmp(pass, "1234") == 0) {
    OpenDoor();
    Serial.println("\nCorrect Password");
    int lightLevel = analogRead(LDR_pin);
    Serial.print("Light level: ");
    Serial.println(lightLevel);
    controlLight(lightLevel);

    float temperature = GetTemp();
    Serial.print("Temperature: ");
    Serial.println(temperature);
    displayTempOnRGB(temperature);
    controlFanSpeed(temperature); 

    delay(5000);
  } else {
    Serial.println("\nIncorrect Password");
    beebBuzzer();

  }
  
}
