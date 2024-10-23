import serial
import threading
import numpy as np
import time

# ---------------------- Step Counting Variable Zone ---------------------- #
# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Parameters for step detection
STEP_THRESHOLD = 0.4  # Initial threshold for peak detection
MIN_TIME_BETWEEN_STEPS = 300  # Minimum time to wait after a step is counted in milliseconds
MAX_SPIKES_WINDOW = 400  # Max time window to consider multiple spikes in milliseconds

# Parameters for stationary detection
STATIONARY_THRESHOLD = 0.05  # Threshold for detecting stationary position

# Threshold for plot visualization
THRESHOLD_GAP = 3  # Gap for upper threshold
LOWER_THRESHOLD_GAP = 2  # Gap for lower threshold

# Step counting variables
step_count = 0
last_step_time = 0  # Time of the last detected step
crossed_upper_threshold = False  # To check if we have crossed the upper threshold
spike_count = 0  # Count of valid spikes
last_spike_time = 0  # Time of the last valid spike
step_detection_paused_until = 0  # Time until which step detection is paused
gyro_magnitude_data = []  # Store gyroscope magnitudes

# ---------------------- Fall Detection Variable Zone ---------------------- #
# Fall detection parameters
ACCEL_THRESHOLD = 2.0  # G-force threshold for crossing event (2 Gs)
STATIONARY_THRESHOLD_FALL = 1.2  # Below this threshold, we consider the sensor to be stationary
STATIONARY_TIME = 2000  # Time in milliseconds to be stationary to confirm fall (2 seconds)
HIGH_ACCEL_DURATION = 200  # Time in milliseconds to confirm high acceleration (200 ms)
POST_FALL_INACTIVITY_TIME = 4000  # Time in milliseconds to monitor for inactivity after a potential fall (4 seconds)
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

# Function to read serial data for step counting
def read_serial_data_step():
    global step_count, last_step_time, crossed_upper_threshold, spike_count
    global last_spike_time, step_detection_paused_until

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                # Split data using the comma and create a dictionary from it
                data_dict = {item.split(': ')[0]: float(item.split(': ')[1]) for item in line.split(', ')}

                # Parse gyroscope data
                gyro_x = data_dict['GyroX']
                gyro_y = data_dict['GyroY']
                gyro_z = data_dict['GyroZ']

                # Calculate the magnitude of the gyroscope readings
                gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)
                gyro_magnitude_data.append(gyro_magnitude)  # Append magnitude data

                current_time = time.time() * 1000  # Current time in milliseconds

                # Calculate smoothed moving average (SMA) based on the last 20 readings
                if len(gyro_magnitude_data) >= 20:
                    sma = np.mean(gyro_magnitude_data[-20:])  # Calculate SMA
                    upper_threshold = sma + THRESHOLD_GAP  # Set upper threshold based on SMA
                    lower_threshold = sma - LOWER_THRESHOLD_GAP  # Set lower threshold based on SMA
                else:
                    upper_threshold = STEP_THRESHOLD  # Use initial threshold for upper threshold
                    lower_threshold = 0  # Default lower threshold if not enough data

                # Check if step detection is paused
                if current_time < step_detection_paused_until:
                    continue  # Ignore spikes if the step detection is paused

                # Only consider spike crossings
                if gyro_magnitude > upper_threshold and not crossed_upper_threshold:
                    crossed_upper_threshold = True  # Mark upper threshold as crossed
                    spike_count += 1  # Increment spike count
                    last_spike_time = current_time  # Update last spike time

                elif gyro_magnitude < lower_threshold and crossed_upper_threshold:
                    # Step counting logic
                    time_since_last_spike = current_time - last_spike_time
                    
                    # Check if the time since last spike is within the max spikes window
                    if time_since_last_spike < MAX_SPIKES_WINDOW and spike_count >= 2:
                        # Valid step detected
                        step_count += 1
                        print(f"Steps detected: {step_count}")  # Print step count in terminal
                        last_step_time = current_time  # Update the last step time
                        step_detection_paused_until = current_time + MIN_TIME_BETWEEN_STEPS  # Set pause until defined time
                        spike_count = 0  # Reset spike count after a step is counted

                    # Reset crossed state
                    crossed_upper_threshold = False  # Reset the upper crossing flag after checking

                # Reset crossing points when gyro_magnitude is within a threshold for stationary detection
                if abs(gyro_magnitude) < STATIONARY_THRESHOLD:
                    crossed_upper_threshold = False

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Function to read serial data for fall detection
def read_serial_data_fall():
    global above_threshold, fall_in_progress, stationary_start_time, high_accel_start_time
    global post_fall_monitoring, post_fall_start_time

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                # Split data using the comma and create a dictionary from it
                data_dict = {item.split(': ')[0]: float(item.split(': ')[1]) for item in line.split(', ')}

                # Parse accelerometer data
                accel_x = data_dict['AccelX']
                accel_y = data_dict['AccelY']
                accel_z = data_dict['AccelZ']

                # Parse gyroscope data
                gyro_x = data_dict['GyroX']
                gyro_y = data_dict['GyroY']
                gyro_z = data_dict['GyroZ']

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
                if fall_in_progress and accel_g_force < STATIONARY_THRESHOLD_FALL:
                    # If we've been stationary for the required time, detect a fall
                    if current_time - stationary_start_time >= STATIONARY_TIME:
                        print(f"Potential fall detected! Stationary below 1.2Gs for 2 seconds at time {current_time}")
                        post_fall_monitoring = True  # Start monitoring for inactivity post-fall
                        post_fall_start_time = current_time  # Track time for post-fall monitoring
                        fall_in_progress = False  # Reset after confirming potential fall
                else:
                    # Reset the stationary start time if we're no longer below 1.2Gs
                    stationary_start_time = current_time

                # Step 3: Monitor for post-fall inactivity
                if post_fall_monitoring:
                    if accel_g_force < STATIONARY_THRESHOLD_FALL and gyro_magnitude < GYRO_THRESHOLD:
                        if current_time - post_fall_start_time >= POST_FALL_INACTIVITY_TIME:
                            print(f"Confirmed fall! No significant movement detected for {POST_FALL_INACTIVITY_TIME / 1000} seconds at time {current_time}")
                            post_fall_monitoring = False  # Reset after confirming fall

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Start threads for data reading
threading.Thread(target=read_serial_data_step, daemon=True).start()
threading.Thread(target=read_serial_data_fall, daemon=True).start()

# Keep the main thread alive to allow for continuous data processing
while True:
    time.sleep(1)  # Sleep for 1 second to keep the main thread alive
