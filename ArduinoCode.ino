#include <Servo.h>
#include "foilsim.h"
foilsim sim(8,9);
String cadena="";
Servo myservo;  // crea el objeto servo
int pos = 0;    // posicion del servo
int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t   mx, my, mz;
float heading;
float tiltheading;
bool error=false;
String error_message="";
int ctr_error=0;
int currentAngle; // Ángulo actual del foil
int foilAngleright=0;
int foilAngleleft=0;
int foilAngleback=0;
float altura=0;
float LONG =0;
float LAT =0;
float SPEED=0;
float pitch=0;
float roll=0;
float SPEED_send =10;
void setup() {
   Serial.begin(57600);
}
 
void loop() {
  // put your main code here, to run repeatedly:
   altura=sim.get_height();
   LONG=sim.get_coord_x();
   LAT= sim.get_coord_y();
   SPEED=sim.get_speed();
   pitch=sim.get_pitch();
   roll=sim.get_roll();
  Serial.print("SPEED= ");
  Serial.println(SPEED);
  Serial.print("LAT= ");
  Serial.println(LAT);
  Serial.print("LONG= ");
  Serial.println(LONG);
  Serial.print("Pitch= ");
  Serial.println(pitch);
  Serial.print("Roll= ");
  Serial.println(roll);
  //TOF Distance
  Serial.print("Altura= ");
  Serial.println(altura);
 

  if (Serial.available() > 0)
   {
      String str = Serial.readStringUntil('#');
      foilAngleback = str.toFloat();
      str = Serial.readStringUntil('#');
      foilAngleleft = str.toFloat();
      str = Serial.readStringUntil('\n');
      foilAngleright = str.toFloat();
      Serial.print("servoBack");
      Serial.println(foilAngleback);
      Serial.print("servoLeft");
      Serial.println(foilAngleleft);
      Serial.print("servoRight");
      Serial.println(foilAngleright);
   
   int correctSpeed=sim.set_motor_speed(SPEED_send);
   int correctBack=sim.set_back_foil_angle(foilAngleback);
   int correctRight=sim.set_front_right_foil_angle(foilAngleright);
   int correctLeft=sim.set_front_left_foil_angle(foilAngleleft);
   if(correctBack==0){
    Serial.println("SET BACK CORRECTO");
   }
   if(correctRight==0){
    Serial.println("SET RIGHT CORRECTO");
   }
   if(correctLeft==0){
    Serial.println("SET LEFT CORRECTO");
   }
   if(correctSpeed==0){
    Serial.println("SET SPEED CORRECTO");
   }
       
      }
}
