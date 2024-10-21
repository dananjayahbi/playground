import serial
import numpy as np
import time

# ---------------------- Variable Zone ---------------------- #
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

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data and count steps
def read_serial_data():
    global step_count, last_step_time, crossed_upper_threshold, spike_count
    global last_spike_time, step_detection_paused_until

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                data = line.split(',')

                # Ensure we have enough data points in the split line
                if len(data) < 4:  # Expecting at least 3 gyro readings
                    print(f"Skipping malformed line: {line}")
                    continue

                # Assuming GyroX, GyroY, and GyroZ data are in the correct indices
                gyro_x = float(data[1].split(':')[-1].strip())
                gyro_y = float(data[2].split(':')[-1].strip())
                gyro_z = float(data[3].split(':')[-1].strip())

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

if __name__ == "__main__":
    print("Starting step counter...")
    read_serial_data()
