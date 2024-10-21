import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np
import time

# ---------------------- Variable Zone ---------------------- #
# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Parameters for step detection
STEP_THRESHOLD = 0.4  # Initial threshold for peak detection
PEAK_HEIGHT_THRESHOLD = 0.4  # Minimum height for a peak
MIN_TIME_BETWEEN_STEPS = 300  # Minimum time to wait after a step is counted in milliseconds
MAX_SPIKES_WINDOW = 400  # Max time window to consider multiple spikes in milliseconds

# Parameters for stationary detection
STATIONARY_THRESHOLD = 0.05  # Threshold for detecting stationary position

# Threshold for plot visualization
THRESHOLD_GAP = 3  # Gap between SMA and upper threshold
LOWER_THRESHOLD_GAP = 2  # Gap between SMA and lower threshold

# ----------------------------------------------------------- #

# Lists to store data
time_data = []
gyro_magnitude_data = []
sma_data = []  # Store the smoothed moving average data

# Step counting variables
step_count = 0
last_step_time = 0  # Time of the last detected step
crossed_upper_threshold = False  # To check if we have crossed the upper threshold
spike_count = 0  # Count of valid spikes
last_spike_time = 0  # Time of the last valid spike
step_detection_paused_until = 0  # Time until which step detection is paused

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
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

                current_time = time.time() * 1000  # Current time in milliseconds
                time_data.append(current_time)  # Append current time in milliseconds
                gyro_magnitude_data.append(gyro_magnitude)  # Append magnitude data

                # Calculate smoothed moving average (SMA)
                if len(gyro_magnitude_data) >= 20:
                    sma = np.mean(gyro_magnitude_data[-20:])  # Calculate SMA based on the last 20 readings
                    sma_data.append(sma)
                else:
                    sma_data.append(gyro_magnitude)  # If less than 20 readings, just append current gyro_magnitude

                # Step detection logic based on fixed upper and lower thresholds
                if len(sma_data) > 0:
                    upper_threshold = sma_data[-1] + THRESHOLD_GAP  # Set upper threshold based on SMA
                    lower_threshold = sma_data[-1] - LOWER_THRESHOLD_GAP  # Set lower threshold based on SMA

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

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Gyroscope Magnitude', color='blue', linewidth=1)  # Thinner line for gyro magnitude
sma_line, = ax.plot([], [], label='SMA', color='orange', linewidth=1)  # SMA line in orange
upper_threshold_line, = ax.plot([], [], color='red', linestyle='-', linewidth=1, label='Upper Threshold')  # Upper threshold line
lower_threshold_line, = ax.plot([], [], color='green', linestyle='-', linewidth=1, label='Lower Threshold')  # Lower threshold line

# Text annotation for step count
step_count_text = ax.text(0.5, 1.05, 'Steps: 0', ha='center', va='bottom', fontsize=12, transform=ax.transAxes)

def init():
    ax.set_xlim(0, 100)  # Set x-axis limits
    ax.set_ylim(-1, 1)   # Set initial y-axis limits for Gyro Magnitude (will adjust dynamically)
    ax.set_ylabel('Gyroscope Magnitude Values')
    ax.set_xlabel('Time (arbitrary units)')
    ax.legend()
    ax.margins(y=0.1)  # Add margins to y-axis
    ax.tick_params(labelsize=10)  # Adjust tick label size
    plt.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.85)  # Adjust margins for axis labels
    return line1, sma_line, upper_threshold_line, lower_threshold_line, step_count_text

def update_plot(frame):
    # Update the plot with the latest data
    if len(time_data) > 0:
        # Update line for gyroscope magnitude data
        line1.set_data(time_data, gyro_magnitude_data)

        # Update line for smoothed moving average
        if len(sma_data) > 0:
            sma_x_data = time_data[-len(sma_data):]  # Corresponding time data for SMA
            sma_line.set_data(sma_x_data, sma_data)  # Update SMA line
        else:
            sma_line.set_data([], [])  # Clear SMA line if no data

        # Update the threshold lines based on the latest SMA
        if len(sma_data) > 0:
            upper_threshold = sma_data[-1] + THRESHOLD_GAP
            lower_threshold = sma_data[-1] - LOWER_THRESHOLD_GAP
            upper_threshold_line.set_data(time_data, [upper_threshold] * len(time_data))  # Set upper threshold line
            lower_threshold_line.set_data(time_data, [lower_threshold] * len(time_data))  # Set lower threshold line
        else:
            # If no SMA data, set default thresholds
            upper_threshold_line.set_data(time_data, [STEP_THRESHOLD] * len(time_data))
            lower_threshold_line.set_data(time_data, [0] * len(time_data))

        # Adjust x-axis limits if necessary
        ax.set_xlim(max(0, len(time_data) - 100), len(time_data))

        # Dynamically adjust y-axis limits to accommodate both the gyro data and threshold lines
        y_min = min(min(gyro_magnitude_data[-100:]), lower_threshold) - 0.1 if len(gyro_magnitude_data) > 100 else min(min(gyro_magnitude_data), lower_threshold) - 0.1
        y_max = max(max(gyro_magnitude_data[-100:]), upper_threshold) + 0.1 if len(gyro_magnitude_data) > 100 else max(max(gyro_magnitude_data), upper_threshold) + 0.1
        ax.set_ylim(y_min, y_max)

        # Update step count display
        step_count_text.set_text(f'Steps: {step_count}')

    return line1, sma_line, upper_threshold_line, lower_threshold_line, step_count_text

# Start threads for data reading and animation
threading.Thread(target=read_serial_data, daemon=True).start()
ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=False)  # Disable blitting
plt.show()