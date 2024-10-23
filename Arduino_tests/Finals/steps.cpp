#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

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

// Variables for moving average
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

  // Calculate gyroscope magnitude
  float gyro_magnitude = sqrt(gyro.gyro.x * gyro.gyro.x + gyro.gyro.y * gyro.gyro.y + gyro.gyro.z * gyro.gyro.z);
  unsigned long current_time = millis(); // Current time in milliseconds

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

  delay(100); // Small delay for smoothing
}
