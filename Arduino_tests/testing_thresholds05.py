import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np

# ---------------------- Variable Zone ---------------------- #
# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Parameters for step detection
STEP_THRESHOLD = 0.4  # Initial threshold for peak detection
PEAK_HEIGHT_THRESHOLD = 0.4  # Minimum height for a peak
MIN_TIME_BETWEEN_STEPS = 600  # Minimum time between steps in milliseconds
MAX_VELOCITY_THRESHOLD = 2.0  # Maximum allowed change in magnitude per update
# Added cooldown to prevent multiple counts for high movements
COOLDOWN_TIME = 1000  # Cooldown time in milliseconds after a step is detected

# Parameters for stationary detection
STATIONARY_THRESHOLD = 0.05  # Threshold for detecting stationary position

# Threshold for plot visualization
THRESHOLD_GAP = 3  # Increased fixed gap between SMA and threshold
WINDOW_SIZE = 20  # Number of readings to calculate the moving average
# ----------------------------------------------------------- #

# Lists to store data
time_data = []
gyro_magnitude_data = []
sma_data = []  # Store the smoothed moving average data

# Step counting variables
step_count = 0
last_step_time = 0  # Time of the last detected step
last_crossing_point = None  # Store last crossing point to avoid double counting
crossed_upward = False  # To check if the last crossing was upward
last_magnitude = 0.0  # To keep track of the last magnitude for velocity calculations

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    global step_count, last_step_time, last_crossing_point, crossed_upward, last_magnitude

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

                current_time = len(time_data)  # Use the length as a pseudo-time
                time_data.append(current_time)  # Incremental time
                gyro_magnitude_data.append(gyro_magnitude)  # Append magnitude data

                # Calculate smoothed moving average (SMA)
                if len(gyro_magnitude_data) >= WINDOW_SIZE:
                    sma = np.mean(gyro_magnitude_data[-WINDOW_SIZE:])  # Calculate SMA based on the last 20 readings
                    sma_data.append(sma)
                else:
                    sma_data.append(gyro_magnitude)  # If less than 20 readings, just append current gyro_magnitude

                # Step detection logic based on threshold crossings
                if len(sma_data) > 0:
                    dynamic_threshold = sma_data[-1] + THRESHOLD_GAP  # Set threshold based on SMA

                    # Calculate velocity (change in magnitude)
                    velocity = abs(gyro_magnitude - last_magnitude)

                    if gyro_magnitude > dynamic_threshold and (last_crossing_point is None or not crossed_upward):
                        # A crossing point occurs when gyro_magnitude crosses above the threshold
                        crossed_upward = True
                        last_crossing_point = current_time  # Update the crossing point

                    elif gyro_magnitude < dynamic_threshold and (last_crossing_point is not None and crossed_upward):
                        # A crossing point occurs when gyro_magnitude crosses below the threshold
                        crossed_upward = False

                        # Check if enough time has passed since the last detected step
                        if (current_time - last_step_time) * 1000 > MIN_TIME_BETWEEN_STEPS:  # Convert to milliseconds
                            # Only count as a step if we are not stationary, above the height threshold,
                            # and within allowed velocity limits
                            if abs(gyro_magnitude) > PEAK_HEIGHT_THRESHOLD and velocity < MAX_VELOCITY_THRESHOLD:
                                step_count += 1
                                print(f"Steps detected: {step_count}")  # Print step count in terminal
                                last_step_time = current_time  # Update the last step time

                    # Reset crossing point when gyro_magnitude is within a threshold for stationary detection
                    if abs(gyro_magnitude) < STATIONARY_THRESHOLD:
                        last_crossing_point = None

                # Update the last magnitude for velocity calculations
                last_magnitude = gyro_magnitude

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Gyroscope Magnitude', color='blue', linewidth=1)  # Thinner line for gyro magnitude
sma_line, = ax.plot([], [], label='SMA', color='orange', linewidth=1)  # SMA line in orange
threshold_line, = ax.plot([], [], color='red', linestyle='-', linewidth=1, label='Dynamic Threshold')  # Dynamic threshold line

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
    return line1, sma_line, threshold_line, step_count_text

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

        # Update the threshold line based on the latest SMA
        if len(sma_data) > 0:
            dynamic_threshold = sma_data[-1] + THRESHOLD_GAP
            threshold_line.set_data(time_data, [dynamic_threshold] * len(time_data))  # Set threshold line
        else:
            # If no SMA data, set a default threshold
            threshold_line.set_data(time_data, [STEP_THRESHOLD] * len(time_data))

        # Adjust x-axis limits if necessary
        ax.set_xlim(max(0, len(time_data) - 100), len(time_data))

        # Dynamically adjust y-axis limits to accommodate both the gyro data and threshold line
        y_min = min(min(gyro_magnitude_data[-100:]), dynamic_threshold) - 0.1 if len(gyro_magnitude_data) > 100 else min(min(gyro_magnitude_data), dynamic_threshold) - 0.1
        y_max = max(max(gyro_magnitude_data[-100:]), dynamic_threshold) + 0.1 if len(gyro_magnitude_data) > 100 else max(max(gyro_magnitude_data), dynamic_threshold) + 0.1
        ax.set_ylim(y_min, y_max)

        # Update the text annotation for step count
        step_count_text.set_text(f'Steps: {step_count}')

    return line1, sma_line, threshold_line, step_count_text

# Start the thread for reading serial data
threading.Thread(target=read_serial_data, daemon=True).start()

# Start the animation for plotting
ani = animation.FuncAnimation(fig, update_plot, init_func=init, interval=100)
plt.show()
