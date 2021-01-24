//#include <Ultrasonic.h>
#include <Separador.h>
#include <Seeed_vl53l0x.h>
#include <Wire.h>
//#include <LiquidCrystal.h>
#include "TinyGPS++.h"
//#include <Stepper.h>
#include <SoftwareSerial.h>
#include <Servo.h>
#include "MPU6050.h"
#include <Grove_I2C_Motor_Driver.h>

#define I2C_ADDRESS 0x0f

//I2Cdev   I2C_M;
TinyGPSPlus gps;
Seeed_vl53l0x VL53L0X;
MPU6050 accelgyro;
VL53L0X_RangingMeasurementData_t RangingMeasurementData;
SoftwareSerial SoftSerial(2, 3);
//Ultrasonic ultrasonic(7);
//unsigned char buffer[64];                   // buffer array for data receive over serial port
//int count = 0;
//String cadena="";
Servo myservoCentral;  // crea el objeto servo central
Servo myservoRight;  // crea el objeto servo right
Servo myservoLeft;  // crea el objeto servo left
//int pos = 0;    // posicion del servo
int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t   mx, my, mz;
//float heading;
//float tiltheading;
float pitch,pitchviejo;
float roll,rollviejo;
float Axyz[3];
//float Gxyz[3];
//float Mxyz[3];
bool error=false;
String error_message="";
//int ctr_error=0;
Separador s;

void setup() {
  Serial.begin(57600);
  while (!Serial);
  SoftSerial.begin(57600);
 
  
  //SETUP del motor (no habria que añadir nada mas)
  //Motor.StepperRun(512);

  //setup IMU
  Wire.begin();
  accelgyro.initialize();

  //setup del sensor optico
  setupVL53L0X();

  //setup del servo
  myservoCentral.attach(3);
  myservoRight.attach(4);
  myservoLeft.attach(5);
  Serial.flush();
}


void loop() {
    
  //  Medida GPS
  while (SoftSerial.available() > 0){
  gps.encode(SoftSerial.read());
  if (gps.altitude.isUpdated())
  error=false;
  }

  //Medida Optica
  getOpticalData();
  
  //Medida IMU
  getAccel_Data();
  getTiltHeading();


  //GPS
  Serial.print("SPEED= ");
  Serial.println(gps.speed.kmph(),2);
  Serial.flush();
  Serial.print("LAT= "); 
  Serial.println(gps.location.lat(),2);
  Serial.flush();
  Serial.print("LONG= ");
  Serial.println(gps.location.lng(),2);
  Serial.flush();
  Serial.print("ALT= "); 
  Serial.println(gps.altitude.meters(),2);
  Serial.flush();
  //IMU
  if((pitch)=='\0' || isnan(pitch)){
  Serial.print("Pitch= ");
  Serial.println(pitchviejo);
  Serial.flush();}
  else{
    Serial.print("Pitch= ");
    Serial.println(pitch);
  Serial.flush();
  pitchviejo=pitch;
  }
  
  if((roll)=='\0' || isnan(roll)){
  Serial.print("Roll= ");
  Serial.println(rollviejo);
  Serial.flush();}
  else{
    Serial.print("Roll= ");
    Serial.println(roll);
  Serial.flush();
  rollviejo=roll;
  }

  //Height
   if(error) {Serial.println(error_message);
  Serial.flush();}
  else{
     Serial.print("Altura= ");
    Serial.println(RangingMeasurementData.RangeMilliMeter);
  Serial.flush();
    
  }
 /* 
  //TOF Distance

     Serial.print("Altura= ");
    Serial.println(ultrasonic.MeasureInCentimeters() * 10);
  Serial.flush();
   

  */
  SoftSerial.flush();
  Serial.flush();

if (Serial.available() > 0) {
  String posServoString=Serial.readStringUntil('\n');
  posServoString.trim();

  //separar por '#'
  int posServoCentral=s.separa(posServoString,'#',0).toInt();
  int posServoLeft=s.separa(posServoString,'#',1).toInt();
  int posServoRight=s.separa(posServoString,'#',2).toInt();


    //Envio hacia el servo y los foils 
    myservoCentral.write(posServoCentral);
    myservoLeft.write(posServoLeft);
    myservoRight.write(posServoRight);
    
    /*
    Serial.flush();
     Serial.print("ServoCentral= ");
    Serial.println(posServoCentral);
    Serial.flush();
     Serial.print("ServoLeft= ");
    Serial.println(posServoLeft);
    Serial.flush();
     Serial.print("ServoRight= ");
    Serial.println(posServoRight);
    Serial.flush();
    SoftSerial.flush();
    */
}
}

void getTiltHeading(void) {
  pitch = asin(-Axyz[0]);
  roll = asin(Axyz[1] / cos(pitch));
}

void getAccel_Data(void) {
  accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
  Axyz[0] = (double) ax / 16384;
  Axyz[1] = (double) ay / 16384;
  Axyz[2] = (double) az / 16384;
}

void setupVL53L0X(){
  VL53L0X_Error Status = VL53L0X_ERROR_NONE;
  Status = VL53L0X.VL53L0X_common_init();
  if (VL53L0X_ERROR_NONE != Status){
    error = true;
   
  }
  else error = false;
  VL53L0X.VL53L0X_high_speed_ranging_init();
  if (VL53L0X_ERROR_NONE != Status){
    error = true;
   
  }
  else error = false;

}

void getOpticalData(){
  VL53L0X_Error Status = VL53L0X_ERROR_NONE;
  memset(&RangingMeasurementData, 0, sizeof(VL53L0X_RangingMeasurementData_t));
  Status = VL53L0X.PerformSingleRangingMeasurement(&RangingMeasurementData);
  if (VL53L0X_ERROR_NONE == Status) {
    if (RangingMeasurementData.RangeMilliMeter >= 1500){
      error = true;
      error_message = "out of range!!"; 
    }
    else error = false;
  }
  else {
    error = true;
    error_message = "mesurement failed";
  }
}
