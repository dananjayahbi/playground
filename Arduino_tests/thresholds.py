import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import threading

# Configuration
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Lists to store data
time_data = []
gyro_y_data = []
step_count_data = []
step_markers = []  # To store indices of steps

# Define threshold for gyroscope
GYRO_THRESHOLD = 0.3  # You can adjust this value dynamically

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line, ignoring errors
        if line:
            # Attempt to parse the gyroscope and step count data
            try:
                gyro_y, step_count = map(float, line.split(','))  # Parse the data
                current_time = len(time_data)  # Use the length as a pseudo-time
                time_data.append(current_time)  # Incremental time
                gyro_y_data.append(gyro_y)  # Append gyroscope data
                step_count_data.append(step_count)  # Append step count data

                # Check if a step was counted (you can adjust the condition as needed)
                if step_count > (step_count_data[-2] if len(step_count_data) > 1 else 0):
                    step_markers.append(current_time)  # Record step occurrence time
            except ValueError:
                # Ignore lines that cannot be converted to float
                print(f"Error parsing line: {line}, skipping...")

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Gyroscope Y', color='blue', linewidth=1)  # Thinner line for gyroscope data
threshold_line = ax.axhline(y=GYRO_THRESHOLD, color='red', linestyle='-', linewidth=1, label='Threshold')  # Solid threshold line

# Text annotation for step count
step_count_text = ax.text(0.5, 1.05, 'Steps: 0', ha='center', va='bottom', fontsize=12, transform=ax.transAxes)

def init():
    ax.set_xlim(0, 100)  # Set x-axis limits
    ax.set_ylim(-1, 1)   # Set y-axis limits for Gyro Y
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

        # Update y-axis limits for gyroscope data
        ax.set_ylim(-1, 1)  # Reset Y limits for gyro

        # Update step count text
        current_step_count = step_count_data[-1] if step_count_data else 0
        step_count_text.set_text(f'Steps: {current_step_count}')  # Update step count text

        # Plot step markers (optional, can remove if not needed)
        for marker in step_markers:
            plt.scatter(marker, gyro_y_data[marker], color='green', marker='o')  # Green marker for step count

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
