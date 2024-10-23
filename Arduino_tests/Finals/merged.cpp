#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

Adafruit_MPU6050 mpu;

// Step detection parameters
const int MIN_TIME_BETWEEN_STEPS = 500;  // Minimum time to wait after a step in milliseconds
const int MAX_SPIKES_WINDOW = 500;        // Max time window to consider multiple spikes in milliseconds
const float MOVEMENT_THRESHOLD = 1.15;     // Threshold for detecting significant movement
const float STATIONARY_THRESHOLD = 0.05;  // Threshold for detecting stationary position
const int SMA_WINDOW_SIZE = 15;            // Size of the moving average window

// Step counting variables
volatile int step_count = 0;
unsigned long last_step_time = 0;         // Time of the last detected step
bool crossed_upper_threshold = false;      // To check if we have crossed the upper threshold
unsigned long last_spike_time = 0;         // Time of the last valid spike
unsigned long step_detection_paused_until = 0; // Time until which step detection is paused

// Fall detection parameters
const float ACCEL_THRESHOLD = 3.0; // G-force threshold for crossing event
const float FALL_STATIONARY_THRESHOLD = 1.2; // Below this threshold, we consider the sensor to be stationary
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

// Variables for moving average for step counting
float sma = 0;  // Current moving average
float readings[SMA_WINDOW_SIZE];  // Array for storing readings for moving average
int moving_average_index = 0;  // Current index for moving average array
int count = 0;  // Count of readings

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  while (!Serial) delay(10); // Wait for the serial connection

  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  // Set accelerometer range
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  // Set gyroscope range
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  // Set the filter bandwidth
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
}

void loop() {
  // Get new sensor events with the readings
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  // Calculate gyroscope magnitude once for both step counting and fall detection
  float gyro_magnitude = sqrt(gyro.gyro.x * gyro.gyro.x + gyro.gyro.y * gyro.gyro.y + gyro.gyro.z * gyro.gyro.z);
  unsigned long current_time = millis(); // Current time in milliseconds

  // Step counting logic
  // Update moving average
  readings[moving_average_index] = gyro_magnitude;
  moving_average_index = (moving_average_index + 1) % SMA_WINDOW_SIZE;  // Circular buffer
  if (count < SMA_WINDOW_SIZE) {
    count++;
  }
  
  // Calculate the moving average
  sma = 0;
  for (int i = 0; i < count; i++) {
    sma += readings[i];
  }
  sma /= count;

  // Dynamic threshold calculation
  float upper_threshold = sma + MOVEMENT_THRESHOLD; 
  float lower_threshold = sma - MOVEMENT_THRESHOLD;

  // Check if step detection is paused
  if (current_time < step_detection_paused_until) {
    // Check for falls regardless
    detectFall(accel, gyro, current_time, gyro_magnitude);
    return; // Ignore spikes if the step detection is paused
  }

  // Detect peaks based on gyroscope magnitude
  if (gyro_magnitude > upper_threshold && !crossed_upper_threshold) {
    crossed_upper_threshold = true; // Mark upper threshold as crossed
    last_spike_time = current_time; // Update last spike time
  } 
  else if (gyro_magnitude < lower_threshold && crossed_upper_threshold) {
    // Step counting logic
    unsigned long time_since_last_spike = current_time - last_spike_time;

    // Check if time since last spike is within max spikes window
    if (time_since_last_spike < MAX_SPIKES_WINDOW) {
      // Validate step detection with time constraint
      if ((current_time - last_step_time) > MIN_TIME_BETWEEN_STEPS) {
        step_count++; // Increment step count
        Serial.print("Step detected! Total steps: ");
        Serial.println(step_count); // Print step count in the Serial Monitor
        last_step_time = current_time; // Update the last step time
        step_detection_paused_until = current_time + MIN_TIME_BETWEEN_STEPS; // Set pause until defined time
      }
    }
    crossed_upper_threshold = false; // Reset the upper crossing flag
  }

  // Reset crossing points when gyro_magnitude is within a threshold for stationary detection
  if (abs(gyro_magnitude) < STATIONARY_THRESHOLD) {
    crossed_upper_threshold = false;
  }

  // Check for falls
  detectFall(accel, gyro, current_time, gyro_magnitude);

  delay(100); // Small delay for smoothing
}

void detectFall(sensors_event_t accel, sensors_event_t gyro, unsigned long current_time, float gyro_magnitude) {
  float accel_x = accel.acceleration.x;
  float accel_y = accel.acceleration.y;
  float accel_z = accel.acceleration.z;

  float accel_magnitude = sqrt(pow(accel_x, 2) + pow(accel_y, 2) + pow(accel_z, 2));
  float accel_g_force = accel_magnitude / 9.8; // Convert to G-force

  // Removed the printing of G-force
  // Serial.print("Accel G-Force: ");
  // Serial.println(accel_g_force);
  
  // High acceleration detection
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

  // Stationary state monitoring after potential fall
  if (fall_in_progress && accel_g_force < FALL_STATIONARY_THRESHOLD) {
    if (current_time - stationary_start_time >= STATIONARY_TIME) {
      post_fall_monitoring = true;
      post_fall_start_time = current_time;
      fall_in_progress = false;
      Serial.println("Potential fall detected! Monitoring for inactivity.");
    }
  } else {
    stationary_start_time = current_time;
  }

  // Post-fall inactivity monitoring
  if (post_fall_monitoring) {
    if (accel_g_force < FALL_STATIONARY_THRESHOLD && gyro_magnitude < GYRO_THRESHOLD) {
      if (current_time - post_fall_start_time >= POST_FALL_INACTIVITY_TIME) {
        Serial.println("Confirmed fall!");
        post_fall_monitoring = false;
      }
    }
  }
}
