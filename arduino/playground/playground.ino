// todo
// fix Vcc wire on test teensy
// figure out how to make teensy fail safe (how to recover from error? maybe reset button)
// how many swings in a game of bowling
// blinking #number of errors?
// error if SD card size < size needed? (need to get this threshhold)

#include <SD.h>
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
 
#define LED_PIN      11   // pin of on-board LED
#define BUTTON_PIN   17   // the record button
#define RECORD_LIMIT 5000 // time in milliseconds for swing record time
#define MAX_SWINGS   5    // how many swings we will record on the SD card

MPU6050 mpu;

int button_state = 0;         // current state of the button
int last_button_state = 0;    // previous state of the button

bool error = false; // used to signify error

uint8_t  swing_count = 1; // keeps track of which swing we are on
unsigned long record_time;
File     results;

bool record = false; // for when to record swing
// MPU control/status vars
uint8_t  mpu_interrupt_status;   // holds actual interrupt status byte from MPU
uint8_t  device_status;      // return status after each device operation (0 = success, !0 = error)
uint16_t packet_size;    // expected DMP packet size (default is 42 bytes)
uint16_t fifo_count;     // count of all bytes currently in FIFO
uint8_t  fifo_buffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
//VectorInt16 aa;         // [x, y, z]            accel sensor measurements
//VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
//VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
//VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
//float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector


// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
  // configure error LED for output
  pinMode(LED_PIN, OUTPUT);
  // configure an actual input for a button
  pinMode(BUTTON_PIN, INPUT);
  // necessary for SD library to work
  pinMode(10, OUTPUT);
  
  Wire.begin();
  Serial.begin(57600);
  Serial.println(F("~~~~~~~~~~~~ I2C SETUP ~~~~~~~~~~~~~~~~"));
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));
  delay(2000); // wait for ready
  Serial.println(F("~~~~~~~~~~~ ACCEL SETUP ~~~~~~~~~~~~~~~"));
  Serial.println(F("Initializing DMP..."));
  device_status = mpu.dmpInitialize();
  // make sure it worked (returns 0 if so)
  if (device_status == 0) {
      Serial.println(F("Enabling DMP..."));
      mpu.setDMPEnabled(true);
      Serial.println(F("DMP ready! Waiting for first interrupt..."));
      // get expected DMP packet size for later comparison
      packet_size = mpu.dmpGetFIFOPacketSize();
  } else {
      // ERROR!
      // 1 = initial memory load failed
      // 2 = DMP configuration updates failed
      // (if it's going to break, usually the code will be 1)
      Serial.print(F("DMP Initialization failed (code "));
      Serial.print(device_status);
      Serial.println(F(")"));
      error = true;
  }
  Serial.println(F("~~~~~~~~~~~~~ SD SETUP ~~~~~~~~~~~~~~~~"));
  // if we have not had an error yet, continue to SD setup
  if (!error) {
    // hang and blink LED to convey SD insertion
    while (true) {
      if (!SD.begin(0)) {
        Serial.println("Insert SD card.");
        if (!error) {
          digitalWrite(LED_PIN, HIGH); 
          error = true;
          delay(500);
        } else {
          digitalWrite(LED_PIN, LOW); 
          error = false;
          delay(500);
        }
      } else {
        break;
      }
    }
    // remove old files
    SD.remove("1.TXT"); SD.remove("2.TXT");
    SD.remove("3.TXT"); SD.remove("4.TXT");
    SD.remove("5.TXT");
    Serial.println("SD card initialization done.");
    results = SD.open("1.txt", FILE_WRITE); // first swing
    if (!results) {
      Serial.println("error opening file on SD card!");
      error = true;
    } else {
      error = false; 
    }
  } else {
    Serial.println("SD card cannot start due to previous errors.");
  }
  Serial.println(F("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"));
}

// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
  // if setup failed, turn on error LED and exit
  if (error) {
      digitalWrite(LED_PIN, HIGH);
      return;
  } else {
      digitalWrite(LED_PIN, LOW);
  }
  
  // read from button pin
  button_state = digitalRead(BUTTON_PIN);

  // compare the button State to its previous state if not recording
  if (!record) {
   if (button_state != last_button_state) {
      if (button_state == HIGH) {
        // set flag and get start of swing recording
        Serial.println(F("RECORDING..."));
        record = true;
        record_time = millis();
      } 
    }
    // save the current state as the last state
    last_button_state = button_state; 
  } else {
    // see if we are done recording
    if ((millis() - record_time) >= RECORD_LIMIT) {
      record = false;
      Serial.println(F("DONE RECORDING"));
      swing_count++; // make next swing
      // close SD card file
      results.close();
      // try to open another file on SD card
      if (swing_count > MAX_SWINGS) {
        error = true; 
        return; // exit CALL setup() !?!?!?!?!?
      } else {
        switch (swing_count) {
          case 2:
            results = SD.open("2.txt", FILE_WRITE);
            break;
          case 3:
            results = SD.open("3.txt", FILE_WRITE);
            break;
          case 4:
            results = SD.open("4.txt", FILE_WRITE);
            break;
          case 5:
            results = SD.open("5.txt", FILE_WRITE);
            break;
        }
        if (!results) {
          error = true;
          return; // exit
        }
      }
    // else, we are recording!
    } else {
      // get INT_STATUS byte
      mpu_interrupt_status = mpu.getIntStatus();
      // get current FIFO count
      fifo_count = mpu.getFIFOCount();
      // check for overflow (this should never happen unless our code is too inefficient)
      if ((mpu_interrupt_status & 0x10) || fifo_count == 1024) {
          // reset so we can continue cleanly
          mpu.resetFIFO();
      // otherwise, check for DMP data ready interrupt (this should happen frequently)
      } else if (mpu_interrupt_status & 0x02) {
        // wait for correct available data length, should be a VERY short wait
        while (fifo_count < packet_size) {
          fifo_count = mpu.getFIFOCount();
        }
        // read a packet from FIFO
        mpu.getFIFOBytes(fifo_buffer, packet_size);
        // track FIFO count here in case there is > 1 packet available
        // (this lets us immediately read more without waiting for an interrupt)
        fifo_count -= packet_size;
        // display quaternion values in easy matrix form: x y z
        mpu.dmpGetQuaternion(&q, fifo_buffer);
        // display initial world-frame acceleration, adjusted to remove gravity
        // and rotated based on known orientation from quaternion
        //mpu.dmpGetAccel(&aa, fifo_buffer);
        //mpu.dmpGetGravity(&gravity, &q);
        //mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
        // display Euler angles in degrees!
        mpu.dmpGetEuler(euler, &q);
        // make a string for assembling the data to log:
        String data_string = "";
        // 1) add time since program running (in milliseconds)
        data_string += String(millis());
        data_string += ",";
        // 2) x, y, and z
        data_string += String(q.x);
        data_string += ",";
        data_string += String(q.y);
        data_string += ",";
        data_string += String(q.z);
        data_string += ",";
        // 3) acceleration in x, y, and z direction
       // data_string += String(aaWorld.x);
       // data_string += ",";
       // data_string += String(aaWorld.y);
       // data_string += ",";
       // data_string += String(aaWorld.z);
       // data_string += ",";
        // 4) euler angles (in degrees) [psi, theta, phi]
        data_string += String(euler[0] * 180/M_PI);
        data_string += ",";
        data_string += String(euler[1] * 180/M_PI);
        data_string += ",";
        data_string += String(euler[2] * 180/M_PI);
        // write data to SD card file
        results.println(data_string);
      }
    }
  }
}
