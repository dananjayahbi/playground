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

# Fall detection parameters
ACCEL_THRESHOLD = 2.0  # G-force threshold for a fall (2 Gs)

# Lists to store data
time_data = []
accel_magnitude_data = []

# Fall detection variables
above_threshold = False  # Flag to track if we're above 2Gs

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    global above_threshold

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                data = line.split(',')

                # Ensure we have enough data points in the split line
                if len(data) < 7:  # Expecting at least 6 readings (AccelX, AccelY, AccelZ)
                    print(f"Skipping malformed line: {line}")
                    continue

                # Parse accelerometer data
                accel_x = float(data[1].split(':')[-1].strip())
                accel_y = float(data[2].split(':')[-1].strip())
                accel_z = float(data[3].split(':')[-1].strip())

                # Calculate the magnitude of acceleration
                accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

                # Convert magnitude to G-force (1G = 9.8 m/s²)
                accel_g_force = accel_magnitude / 9.8

                current_time = time.time() * 1000  # Current time in milliseconds
                time_data.append(current_time)
                accel_magnitude_data.append(accel_g_force)  # Store G-force magnitude

                # Simplified fall detection: crossing above and below 2Gs
                if accel_g_force > ACCEL_THRESHOLD and not above_threshold:
                    print(f"Crossed above 2Gs: {accel_g_force} Gs at time {current_time}")
                    above_threshold = True  # Mark that we've crossed above the threshold

                elif accel_g_force < ACCEL_THRESHOLD and above_threshold:
                    print(f"Fall detected! Crossed below 2Gs: {accel_g_force} Gs at time {current_time}")
                    above_threshold = False  # Reset the threshold flag after detecting a fall

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
accel_line, = ax.plot([], [], label='Accelerometer Magnitude (Gs)', color='blue', linewidth=1)
accel_threshold_line, = ax.plot([], [], color='red', linestyle='--', linewidth=1, label='Accel Threshold (2 Gs)')

# Text annotation for fall detection
fall_detected_text = ax.text(0.5, 1.05, 'No Fall', ha='center', va='bottom', fontsize=12, transform=ax.transAxes)

def init():
    ax.set_xlim(0, 100)  # Set x-axis limits
    ax.set_ylim(0, 5)  # Set y-axis limits
    ax.set_ylabel('G-Force (Gs)')
    ax.set_xlabel('Time (arbitrary units)')
    ax.legend()
    ax.margins(y=0.1)
    plt.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.85)
    return accel_line, accel_threshold_line, fall_detected_text

def update_plot(frame):
    if len(time_data) > 0:
        accel_line.set_data(range(len(time_data)), accel_magnitude_data)

        # Threshold line (constant)
        accel_threshold_line.set_data(range(len(time_data)), [ACCEL_THRESHOLD] * len(time_data))

        # Update x-axis limits dynamically
        ax.set_xlim(max(0, len(time_data) - 100), len(time_data))

        # Adjust y-axis dynamically to include the accel data
        y_min = min(accel_magnitude_data[-100:]) - 0.5
        y_max = max(accel_magnitude_data[-100:]) + 0.5
        ax.set_ylim(y_min, y_max)

    return accel_line, accel_threshold_line, fall_detected_text

# Start threads for data reading and animation
threading.Thread(target=read_serial_data, daemon=True).start()
ani = animation.FuncAnimation(fig, update_plot, init_func=init, interval=100)
plt.show()
