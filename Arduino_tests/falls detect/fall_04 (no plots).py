import serial
import threading
import numpy as np
import time

# ---------------------- Variable Zone ---------------------- #
# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Fall detection parameters
ACCEL_THRESHOLD = 2.0  # G-force threshold for crossing event (2 Gs)
STATIONARY_THRESHOLD = 1.2  # Below this threshold, we consider the sensor to be stationary
STATIONARY_TIME = 2000  # Time in milliseconds to be stationary to confirm fall (2 seconds)
HIGH_ACCEL_DURATION = 200  # Time in milliseconds to confirm high acceleration (200 ms)
POST_FALL_INACTIVITY_TIME = 4000  # Time in milliseconds to monitor for inactivity after a potential fall (5 seconds)
GYRO_THRESHOLD = 50  # Gyroscope threshold for inactivity (50 degrees/s)

# Fall detection variables
above_threshold = False  # Flag to track if we're above 2Gs
fall_in_progress = False  # To track if we're monitoring for a potential fall
stationary_start_time = 0  # Time when stationary state starts
high_accel_start_time = 0  # Time when high acceleration starts
post_fall_monitoring = False  # Flag for post-fall inactivity monitoring
post_fall_start_time = 0  # Start time for post-fall inactivity monitoring

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    global above_threshold, fall_in_progress, stationary_start_time, high_accel_start_time
    global post_fall_monitoring, post_fall_start_time

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                data = line.split(',')

                # Ensure we have enough data points in the split line
                if len(data) < 7:  # Expecting at least 6 readings (AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ)
                    print(f"Skipping malformed line: {line}")
                    continue

                # Parse accelerometer data
                accel_x = float(data[1].split(':')[-1].strip())
                accel_y = float(data[2].split(':')[-1].strip())
                accel_z = float(data[3].split(':')[-1].strip())

                # Parse gyroscope data
                gyro_x = float(data[4].split(':')[-1].strip())
                gyro_y = float(data[5].split(':')[-1].strip())
                gyro_z = float(data[6].split(':')[-1].strip())

                # Calculate the magnitude of acceleration
                accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
                # Calculate the magnitude of gyroscope data (angular velocity)
                gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)

                # Convert acceleration magnitude to G-force (1G = 9.8 m/s²)
                accel_g_force = accel_magnitude / 9.8

                current_time = time.time() * 1000  # Current time in milliseconds

                # Step 1: Simplified fall detection - crossing above and below 2Gs
                if accel_g_force > ACCEL_THRESHOLD:
                    if not above_threshold:
                        # Mark the start of high acceleration
                        high_accel_start_time = current_time
                    above_threshold = True  # We're above the threshold

                elif accel_g_force < ACCEL_THRESHOLD and above_threshold:
                    # Check if we've been above the threshold long enough
                    if current_time - high_accel_start_time >= HIGH_ACCEL_DURATION:
                        print(f"Crossed below 2Gs: {accel_g_force} Gs at time {current_time}")
                        above_threshold = False  # Reset after crossing below threshold
                        fall_in_progress = True  # Start monitoring for stationary state
                        stationary_start_time = current_time  # Track time when it goes below the threshold
                    else:
                        print(f"High acceleration detected but not long enough: {accel_g_force} Gs at time {current_time}")

                # Step 2: Check for stationary state (below 1.2Gs for 2 seconds)
                if fall_in_progress and accel_g_force < STATIONARY_THRESHOLD:
                    # If we've been stationary for the required time, detect a fall
                    if current_time - stationary_start_time >= STATIONARY_TIME:
                        print(f"Potential fall detected! Stationary below 1.2Gs for 2 seconds at time {current_time}")
                        post_fall_monitoring = True  # Start monitoring for post-fall inactivity
                        post_fall_start_time = current_time  # Track time for post-fall monitoring
                        fall_in_progress = False  # Reset after confirming potential fall
                else:
                    # Reset the stationary start time if we're no longer below 1.2Gs
                    stationary_start_time = current_time

                # Step 3: Monitor for post-fall inactivity
                if post_fall_monitoring:
                    if accel_g_force < STATIONARY_THRESHOLD and gyro_magnitude < GYRO_THRESHOLD:
                        if current_time - post_fall_start_time >= POST_FALL_INACTIVITY_TIME:
                            print(f"Confirmed fall! No significant movement detected for {POST_FALL_INACTIVITY_TIME / 1000} seconds at time {current_time}")
                            post_fall_monitoring = False  # Reset after confirming fall

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Start threads for data reading
threading.Thread(target=read_serial_data, daemon=True).start()

# Keep the main thread alive to allow for continuous data processing
while True:
    time.sleep(1)  # Sleep for 1 second to keep the main thread alive
