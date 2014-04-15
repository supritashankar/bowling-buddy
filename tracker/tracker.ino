// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Bowling Buddy: "A hand-tracker for a bowling ball swing"
// Author: Aaron Reyes @ 2014
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

/* ============================================
This code is placed under the MIT license
Copyright (c) 2014 Aaron Reyes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
*/

// todo:
// error if SD card size < size needed? (need to get this threshold)
// button-state = 0 is too sensitive for first press?

// notes:
// use charging push button as reset for error or SD overflow
// 100ohm resistor for green LED
// 100kohm resistor for record button

#include <SD.h>
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
 
/* NOTE: a normal game of 10 frames and frames 1 to 9 having 2 rolls max, with
 *       the last frame having 3 rolls, has 21 max possible swings/rolls. */
#define ERROR_LED_PIN 11    // pin of on-board teensy LED (used for errors)
#define GREEN_LED_PIN 16    // pin of green LED used to signify correct startup
#define BUTTON_PIN    17    // pin of the the record push button
#define RECORD_LIMIT  5000  // time in milliseconds to record swing 
#define MAX_SWINGS    5     // how many swings we will record on the SD card
// NOTE: below numbers found using MPU6050_calibration.ino
#define X_ACCEL_OFF   -1177 // accelerometer X offset
#define Y_ACCEL_OFF   1473  // accelerometer Y offset
#define Z_ACCEL_OFF   1339  // accelerometer Z offset
#define X_GYRO_OFF    -22   // gyroscope X offset
#define Y_GYRO_OFF    8     // gyroscope Y offset
#define Z_GYRO_OFF    165   // gyroscope Z offset

bool error = false; // used to signify specific errors

MPU6050  mpu; // a reference to the accelerometer class
File results; // a reference to a file descriptor on SD card

// Processor state/control vars:
int button_state      = 0; // current state of the push button
int last_button_state = 0; // previous state of the push button
bool blink_state  = false; // a simple flag to flash green LED when ready for SD card
uint8_t  swing_count  = 1; // keeps track of which swing we are on (MAX = 255)
unsigned long record_time; // a marker for the start of a record time
bool record = false;       // a flag to say when we are recording

// MPU state/control vars:
uint8_t  mpu_interrupt_status; // holds actual interrupt status byte from MPU
uint8_t  device_status;        // device status (0 = success, !0 = error)
uint16_t packet_size;          // expected DMP packet size (default is 42 bytes)
uint16_t fifo_count;           // count of all bytes currently in FIFO
uint8_t  fifo_buffer[64];      // FIFO storage buffer

// MPU orientation/motion vars:
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
  pinMode(ERROR_LED_PIN, OUTPUT); // configure error LED for output
  pinMode(GREEN_LED_PIN, OUTPUT); // configure green LED for output
  pinMode(BUTTON_PIN, INPUT);     // configure record button for input
  pinMode(10, OUTPUT);            // necessary for SD library to work
  
  Wire.begin();
  Serial.begin(19200); 
  mpu.initialize();
  device_status = mpu.dmpInitialize();
  mpu.setXGyroOffset(X_GYRO_OFF);
  mpu.setYGyroOffset(Y_GYRO_OFF);
  mpu.setZGyroOffset(Z_GYRO_OFF);
  mpu.setXAccelOffset(X_ACCEL_OFF);
  mpu.setYAccelOffset(Y_ACCEL_OFF);
  mpu.setZAccelOffset(Z_ACCEL_OFF);
  // make sure it worked (returns 0 if so)
  if (device_status == 0) {
      mpu.setDMPEnabled(true);
      // get expected DMP packet size for later comparison
      packet_size = mpu.dmpGetFIFOPacketSize();
  } else {
      error = true;
  }
  // if we have not had an error yet, continue to SD setup
  if (!error) {
    // turn on green LED to signify correct startup
    while (true) {
      if (!SD.begin(0)) { // 0 => teensy 2.0
        // blink LED to ask for SD card
        blink_state = !blink_state;
        digitalWrite(GREEN_LED_PIN, blink_state);
        delay(250); // wait 
      } else {
        break;
      }
    }
    results = SD.open("1.TXT", FILE_WRITE); // first swing
    if (!results) {
      error = true;
    } else {
      digitalWrite(GREEN_LED_PIN, HIGH); // all-clear signal
    }
  }
}

// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
  // check for an error
  if (error) {
    digitalWrite(GREEN_LED_PIN, LOW); // NOT all-clear signal
    // check for overflow of SD card
    if (swing_count > MAX_SWINGS) {
      // flash error LED to user
      blink_state = !blink_state;
      digitalWrite(ERROR_LED_PIN, blink_state);
    } else {
      digitalWrite(ERROR_LED_PIN, HIGH); // hard-reset needed 
    }
    return;
  } else {
    digitalWrite(ERROR_LED_PIN, LOW);
  }
  
  // read from button pin
  button_state = digitalRead(BUTTON_PIN);

  // compare the button State to its previous state if not recording
  if (!record) {
   if (button_state != last_button_state) {
      if (button_state == HIGH) {
        // set flag and get start of swing recording
        Serial.print("start...");
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
      Serial.println("done");
      swing_count++; // make next swing
      // close SD card file
      results.close();
      // try to open another file on SD card
      if (swing_count > MAX_SWINGS) {
        error = true;
        return; 
      } else {
        switch (swing_count) {
          case 2:
            results = SD.open("2.TXT", FILE_WRITE);
            break;
          case 3:
            results = SD.open("3.TXT", FILE_WRITE);
            break;
          case 4:
            results = SD.open("4.TXT", FILE_WRITE);
            break;
          case 5:
            results = SD.open("5.TXT", FILE_WRITE);
            break;
        }
        if (!results) {
          error = true;
          return;
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
        
        mpu.dmpGetQuaternion(&q, fifo_buffer);
        mpu.dmpGetAccel(&aa, fifo_buffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        
        // make a string for assembling the data to log:
        String data_string = "";
        // 1) add time since program running (in milliseconds)
        data_string += String(millis());
        data_string += ",";
        // 2) x, y, and z acceleration
        data_string += String(aaReal.x);
        data_string += ",";
        data_string += String(aaReal.y);
        data_string += ",";
        data_string += String(aaReal.z);
        data_string += ",";
        // 3) yaw, pitch, roll in degrees
        data_string += String(ypr[0] * 180/M_PI); // yaw (z-axis)
        data_string += ",";
        data_string += String(ypr[1] * 180/M_PI); // pitch (y-axis)
        data_string += ",";
        data_string += String(ypr[2] * 180/M_PI); // roll (x-axis)
        // write data to SD card file
        results.println(data_string);
      }
    }
  }
}
