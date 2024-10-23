#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

Adafruit_MPU6050 mpu;

const float ACCEL_THRESHOLD = 6.5; // G-force threshold for crossing event
const float STATIONARY_THRESHOLD = 1.2; // Below this threshold, we consider the sensor to be stationary
const unsigned long STATIONARY_TIME = 2000; // Time to confirm stationary state (2 seconds)
const unsigned long HIGH_ACCEL_DURATION = 200; // Time to confirm high acceleration (200 ms)
const unsigned long POST_FALL_INACTIVITY_TIME = 4000; // Time to monitor for inactivity after a potential fall (4 seconds)
const float GYRO_THRESHOLD = 60.0; // Gyroscope threshold for inactivity (60 degrees/s)

bool above_threshold = false;
bool fall_in_progress = false;
unsigned long stationary_start_time = 0;
unsigned long high_accel_start_time = 0;
bool post_fall_monitoring = false;
unsigned long post_fall_start_time = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) delay(10);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G); // Change to 4G if needed
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  delay(100);
}

void loop() {
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  float accel_x = accel.acceleration.x;
  float accel_y = accel.acceleration.y;
  float accel_z = accel.acceleration.z;

  float gyro_x = gyro.gyro.x;
  float gyro_y = gyro.gyro.y;
  float gyro_z = gyro.gyro.z;

  float accel_magnitude = sqrt(pow(accel_x, 2) + pow(accel_y, 2) + pow(accel_z, 2));
  float gyro_magnitude = sqrt(pow(gyro_x, 2) + pow(gyro_y, 2) + pow(gyro_z, 2));
  float accel_g_force = accel_magnitude / 9.8; // Convert to G-force

  unsigned long current_time = millis();

  if (accel_g_force > ACCEL_THRESHOLD) {
    if (!above_threshold) {
      high_accel_start_time = current_time;
      above_threshold = true;
      Serial.println("High acceleration detected!");
    }
  } else if (accel_g_force < ACCEL_THRESHOLD && above_threshold) {
    if (current_time - high_accel_start_time >= HIGH_ACCEL_DURATION) {
      above_threshold = false;
      fall_in_progress = true;
      stationary_start_time = current_time;
      Serial.println("Acceleration dropped below threshold; monitoring for stationary state.");
    }
  }

  if (fall_in_progress && accel_g_force < STATIONARY_THRESHOLD) {
    if (current_time - stationary_start_time >= STATIONARY_TIME) {
      post_fall_monitoring = true;
      post_fall_start_time = current_time;
      fall_in_progress = false;
      Serial.println("Potential fall detected! Monitoring for inactivity.");
    }
  } else {
    stationary_start_time = current_time;
  }

  if (post_fall_monitoring) {
    if (accel_g_force < STATIONARY_THRESHOLD && gyro_magnitude < GYRO_THRESHOLD) {
      if (current_time - post_fall_start_time >= POST_FALL_INACTIVITY_TIME) {
        Serial.println("Confirmed fall!");
        post_fall_monitoring = false;
      }
    }
  }

  delay(100); // Small delay for smoothing
}
