#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"


#define SAMPLE_RATE_WITHOUT_MPU (15) //milliseconds
#define BAUD_RATE  115200

//Uncomment "OUTPUT_MPU_QUATERNIONS" to send serially quaternions coming from MPU-6050
#define MPU           1

//Uncomment "OUTPUT_BNO1_QUATERNIONS" to send serially quaternions coming from first BNO055
#define BNO1          1

//Uncomment "OUTPUT_BNO2_QUATERNIONS" to send serially quaternions coming from second BNO055
#define BNO2          1

//Uncomment "OUTPUT_EMG1_ANALOG" to send serially analog signal coming from Myoware
#define EMG1_ANALOG   1
//Uncomment "OUTPUT_EMG1_DUMB" to send serially dumb data instead of sensor data
#define EMG1_DUMB     0


Adafruit_BNO055 bno2 = Adafruit_BNO055(55, BNO055_ADDRESS_A); //Use first I2C address
Adafruit_BNO055 bno1 = Adafruit_BNO055(55, BNO055_ADDRESS_B); //Use second I2C address
MPU6050 mpu;


bool dmpReady = false; 
uint8_t mpuIntStatus; 
uint8_t devStatus;    
uint16_t packetSize;    
uint16_t fifoCount;    
uint8_t fifoBuffer[64];
float t = 0;
float t_stamp = 0;
int EMGpin = 0;
int EMGvalue = 0;
float t_init;
float dt;
Quaternion q;
bool noMPUConnected = false;
bool noBNO1 = false;
bool noBNO2 = false;



// ================================================================
// ===               INTERRUPT DETECTION ROUTINE                ===
// ================================================================

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
  mpuInterrupt = true;
}



void setup(void)
{
  ///////////////////////       INITIALIZE Serial and I2C       ///////////////////
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  Wire.begin();
  TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
  Fastwire::setup(400, true);
  #endif
  
  Serial.begin(BAUD_RATE);
  while (!Serial); // wait for Leonardo enumeration, others continue immediately
  

  ///////////////////////       INITIALIZE EMG       ///////////////////
  pinMode(EMGpin, INPUT);    
    t_init = millis();

  ///////////////////////       INITIALIZE 2 IMUs BNO055       ///////////////////
  if(!bno1.begin())
  {
      noBNO1 = true;
  }

  if(!bno2.begin())
  {
     noBNO2 = true;
  }

  delay(1000);

  bno1.setExtCrystalUse(true);
  bno2.setExtCrystalUse(true);
  

  ///////////////////////       INITIALIZE IMU MPU 6050       ///////////////////
  mpu.initialize();

  devStatus = mpu.dmpInitialize();
  noMPUConnected = false;
  // supply your own gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(220);
  mpu.setYGyroOffset(76);
  mpu.setZGyroOffset(-85);
  mpu.setZAccelOffset(1788); // 1688 factory default for my test chip

  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {

    mpu.setDMPEnabled(true);

    // enable Arduino interrupt detection
    attachInterrupt(0, dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // set our DMP Ready flag so the main loop() function knows it's okay to use it
    dmpReady = true;

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
    //Serial.print(F("DMP Initialization failed (code "));
    //Serial.print(devStatus);
    //Serial.println(F(")"));
    noMPUConnected = true;
  }

}

//1 loop with 3 IMUS : 14ms -> 7ms for MPU, 7ms for 2 BNO
void loop(void)
{
  /* Get a new event from BNO055*/
  /*sensors_event_t event;
  bno.getEvent(&event);*/

  ///////////////   Get a new Paket from MPU6050   ////////////////

 if(MPU){

  if(!noMPUConnected)
  {
 // if programming failed, don't try to do anything
  if (!dmpReady) return;

  // MPU interrupt or extra packet(s) available
  //while (!mpuInterrupt && fifoCount < packetSize);

 if (mpuInterrupt || fifoCount >= packetSize)
 {
      // reset interrupt flag and get INT_STATUS byte
      mpuInterrupt = false;
      mpuIntStatus = mpu.getIntStatus();
    
      // get current FIFO count
      fifoCount = mpu.getFIFOCount();
    
      // check for overflow (this should never happen unless our code is too inefficient)
      if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        // reset so we can continue cleanly
        mpu.resetFIFO();
        /*
        Serial.print(fifoCount);
        Serial.print("\t");
        Serial.println(F("FIFO overflow!"));*/
    
        // otherwise, check for DMP data ready interrupt (this should happen frequently)
      } else if (mpuIntStatus & 0x02) {
        // wait for correct available data length, should be a VERY short wait
        while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
    
        // read a packet from FIFO
        mpu.getFIFOBytes(fifoBuffer, packetSize);
    
        // track FIFO count here in case there is > 1 packet available
        // (this lets us immediately read more without waiting for an interrupt)
        fifoCount -= packetSize;
    
        // display quaternion values in easy matrix form: w x y z
          mpu.dmpGetQuaternion(&q, fifoBuffer);
          Serial.print("IMU3");
          Serial.print("\t");
          Serial.print(q.w);
          Serial.print("\t");
          Serial.print(q.x);
          Serial.print("\t");
          Serial.print(q.y);
          Serial.print("\t");
          Serial.println(q.z);
          //Serial.print("\t");

      } 
    }
  }
 }


if(MPU){

    delay(9.5);

}
else{
  if(EMG1_DUMB){
    delay(10);
  }
  else{
    delay(9);
  }
}


  ///////////////// Send data via Serial for BNO055 (betw 5 and 9ms for both) //////////////////
   
   
  if(BNO1){
    if(!noBNO1){
     
    imu::Quaternion quat1 = bno1.getQuat();

    Serial.print("IMU1"); 
    Serial.print("\t");
    Serial.print(quat1.w()); 
    Serial.print("\t");
    Serial.print(quat1.x()); 
    Serial.print("\t");
    Serial.print(quat1.y()); 
    Serial.print("\t");
    Serial.println(quat1.z ()); 
    //Serial.print("\t");
    }
  }

if(MPU){
    delay(9.5);
}
else{
  if(EMG1_DUMB){
    delay(10);
  }
  else{
    delay(9);
  }
}




    
 if(BNO2){
 
  if(!noBNO2){
 
  imu::Quaternion quat2 = bno2.getQuat();
    
  Serial.print("IMU2"); 
  Serial.print("\t");
  Serial.print(quat2.w()); 
  Serial.print("\t");
  Serial.print(quat2.x()); 
  Serial.print("\t");
  Serial.print(quat2.y()); 
  Serial.print("\t");
  Serial.println(quat2.z ()); 
  //Serial.print("\t");
  }
 }

if(MPU){
  if(EMG1_DUMB){
    delay(10);
  }
  else{
    delay(6);
  }
}
else{
  if(EMG1_DUMB){
    delay(13);
  }
}


 /////////////////     Send data via Serial for EMG      //////////////////

  if(EMG1_ANALOG){ 
  EMGvalue = analogRead(EMGpin);

  Serial.print("EMG1"); 
  Serial.print("\t");
  Serial.println(EMGvalue);
  //Serial.print("\t");
  }
  
  if(EMG1_DUMB){
  dt = (millis() - t_init)/1000;
  EMGvalue = 200*sin(dt) + 400;

  Serial.print("EMG1"); 
  Serial.print("\t");
  Serial.println(EMGvalue);
  //Serial.print("\t");
  }


 

 /////////////////     Wait the specified delay before requesting nex data      //////////////////

if(MPU){
  if(EMG1_DUMB){
    delay(6);
  }

}


  dt = millis()-t;
   //Serial.print("     dt:   ");
   //Serial.println(dt);
   t = millis();
}


