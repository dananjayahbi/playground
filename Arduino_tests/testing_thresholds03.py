import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import threading
import time

# ---------------------- Variable Zone ---------------------- #
# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Parameters for step detection
STEP_THRESHOLD = 0.3  # Threshold for peak detection
PEAK_HEIGHT_THRESHOLD = 0.4  # Minimum height for a peak
MIN_TIME_BETWEEN_STEPS = 200  # Minimum time between steps in milliseconds

# Parameters for stationary detection
STATIONARY_THRESHOLD = 0.05  # Threshold for detecting stationary position

# Threshold for plot visualization
GYRO_THRESHOLD = 0.3  # You can adjust this value dynamically
# ----------------------------------------------------------- #

# Lists to store data
time_data = []
gyro_y_data = []
step_count_data = []
step_markers = []  # To store indices of steps

# Step counting variables
step_count = 0
last_step_time = 0  # Time of the last detected step
consecutive_steps = 0
required_consecutive_steps = 5  # Number of consecutive peaks required to confirm a step

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    global step_count, last_step_time, consecutive_steps
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            # Attempt to parse the gyroscope data
            try:
                data = line.split(',')
                
                # Ensure we have enough data points in the split line
                if len(data) < 2:
                    print(f"Skipping malformed line: {line}")
                    continue

                # Assuming GyroY data is the second element (index 1)
                gyro_y = float(data[1].split(':')[-1].strip())  # Extract GyroY data

                current_time = len(time_data)  # Use the length as a pseudo-time
                time_data.append(current_time)  # Incremental time
                gyro_y_data.append(gyro_y)  # Append gyroscope data

                # Step detection logic
                if gyro_y > STEP_THRESHOLD and gyro_y > PEAK_HEIGHT_THRESHOLD:
                    if (current_time - last_step_time) * 1000 > MIN_TIME_BETWEEN_STEPS:  # Convert to milliseconds
                        consecutive_steps += 1  # Count this as a step
                        
                        # Check if we have enough consecutive steps to confirm
                        if consecutive_steps >= required_consecutive_steps:
                            step_count += 1
                            print(f"Steps detected: {step_count}")  # Print step count in terminal
                            consecutive_steps = 0  # Reset counter after counting the step
                        
                        last_step_time = current_time  # Update the last step time
                    else:
                        # If detected too quickly, ignore this peak
                        consecutive_steps = 0  # Reset consecutive step count if time is too short
            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Gyroscope Y', color='blue', linewidth=1)  # Thinner line for gyroscope data
threshold_line = ax.axhline(y=GYRO_THRESHOLD, color='red', linestyle='-', linewidth=1, label='Threshold')  # Solid threshold line

# Text annotation for step count
step_count_text = ax.text(0.5, 1.05, 'Steps: 0', ha='center', va='bottom', fontsize=12, transform=ax.transAxes)

def init():
    ax.set_xlim(0, 100)  # Set x-axis limits
    ax.set_ylim(-1, 1)   # Initial y-axis limits, will be adjusted dynamically
    ax.set_ylabel('Gyroscope Y Values')
    ax.set_xlabel('Time (arbitrary units)')
    ax.legend()
    ax.margins(y=0.1)  # Add margins to y-axis
    ax.tick_params(labelsize=10)  # Adjust tick label size
    plt.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.85)  # Adjust margins for axis labels
    return line1, threshold_line, step_count_text

def update_plot(frame):
    # Update the plot with the latest data
    if len(time_data) > 0:
        # Update line for gyroscope data
        line1.set_data(time_data, gyro_y_data)

        # Adjust x-axis limits if necessary
        ax.set_xlim(max(0, len(time_data) - 100), len(time_data))

        # Dynamically adjust the y-axis limits based on the data
        y_min = min(gyro_y_data) - 0.1  # Add a small margin below the minimum value
        y_max = max(gyro_y_data) + 0.1  # Add a small margin above the maximum value
        ax.set_ylim(y_min, y_max)  # Set dynamic y-limits

        # Update step count text
        step_count_text.set_text(f'Steps: {step_count}')  # Update step count text

    return line1, threshold_line, step_count_text

# Start reading data in a separate thread
thread = threading.Thread(target=read_serial_data)
thread.daemon = True  # Ensure the thread will close when the main program exits
thread.start()

# Maximize the window
plt.get_current_fig_manager().window.state('zoomed')  # For Windows systems, use this to maximize

# Start the animation
ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, cache_frame_data=False)
plt.show()
