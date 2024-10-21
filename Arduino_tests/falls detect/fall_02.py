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
GYRO_THRESHOLD = 150  # Threshold for angular velocity in degrees per second (to detect sudden rotation)
POST_FALL_TIME_WINDOW = 1500  # Time window to check if a person is stationary after high acceleration (in ms)
HIGH_ACCEL_DURATION = 200  # Minimum duration of high acceleration to consider it a fall (in ms)

# Visualization thresholds
ACCEL_VISUAL_THRESHOLD = 2.0  # For visualizing the upper threshold on the plot
GYRO_VISUAL_THRESHOLD = 300  # For visualizing the gyroscope threshold

# Lists to store data
time_data = []
accel_magnitude_data = []
gyro_magnitude_data = []

# Fall detection variables
fall_detected = False
high_accel_start_time = 0  # Track when high acceleration starts
fall_start_time = 0  # Track the potential fall time
post_fall_monitoring = False  # Flag to start post-fall monitoring for inactivity

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Function to read serial data
def read_serial_data():
    global fall_detected, high_accel_start_time, fall_start_time, post_fall_monitoring

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode the serial line
        if line:
            try:
                data = line.split(',')

                # Ensure we have enough data points in the split line
                if len(data) < 7:  # Expecting at least 6 readings (AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ)
                    print(f"Skipping malformed line: {line}")
                    continue

                # Parse accelerometer and gyroscope data
                accel_x = float(data[1].split(':')[-1].strip())
                accel_y = float(data[2].split(':')[-1].strip())
                accel_z = float(data[3].split(':')[-1].strip())
                gyro_x = float(data[4].split(':')[-1].strip())
                gyro_y = float(data[5].split(':')[-1].strip())
                gyro_z = float(data[6].split(':')[-1].strip())

                # Calculate magnitudes for acceleration and gyroscope data
                accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

                # Convert magnitude to G-force (1G = 9.8 m/s²)
                accel_g_force = accel_magnitude / 9.8

                gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)

                current_time = time.time() * 1000  # Current time in milliseconds
                time_data.append(current_time)
                accel_magnitude_data.append(accel_g_force)  # Store G-force magnitude
                gyro_magnitude_data.append(gyro_magnitude)

                # Fall detection logic
                if accel_g_force > ACCEL_THRESHOLD:  # Check if G-force exceeds 2Gs
                    print(f"High acceleration detected: {accel_g_force} Gs at time {current_time}")
                    if high_accel_start_time == 0:
                        high_accel_start_time = current_time  # Mark when high acceleration starts
                    elif current_time - high_accel_start_time > HIGH_ACCEL_DURATION:
                        if gyro_magnitude > GYRO_THRESHOLD:
                            fall_detected = True
                            fall_start_time = current_time  # Mark fall time
                            post_fall_monitoring = True
                            print(f"Fall detected with accel: {accel_g_force} Gs and gyro: {gyro_magnitude} degrees/s")
                else:
                    high_accel_start_time = 0  # Reset high acceleration time if below threshold

                # Monitor for post-fall inactivity
                if post_fall_monitoring:
                    if current_time - fall_start_time > POST_FALL_TIME_WINDOW:
                        if accel_g_force < 1.0 and gyro_magnitude < 50:
                            print("User seems to be stationary after fall, alert!")
                        post_fall_monitoring = False  # Reset monitoring after checking

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Set up the plot
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
accel_line, = ax.plot([], [], label='Accelerometer Magnitude (Gs)', color='blue', linewidth=1)
gyro_line, = ax.plot([], [], label='Gyroscope Magnitude', color='orange', linewidth=1)
accel_threshold_line, = ax.plot([], [], color='red', linestyle='--', linewidth=1, label='Accel Threshold (2 Gs)')
gyro_threshold_line, = ax.plot([], [], color='green', linestyle='--', linewidth=1, label='Gyro Threshold (150 °/s)')

# Text annotation for fall detection
fall_detected_text = ax.text(0.5, 1.05, 'No Fall', ha='center', va='bottom', fontsize=12, transform=ax.transAxes)

def init():
    ax.set_xlim(0, 100)  # Set x-axis limits
    ax.set_ylim(0, 5)  # Set y-axis limits
    ax.set_ylabel('Sensor Magnitude (Gs and °/s)')
    ax.set_xlabel('Time (arbitrary units)')
    ax.legend()
    ax.margins(y=0.1)
    plt.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.85)
    return accel_line, gyro_line, accel_threshold_line, gyro_threshold_line, fall_detected_text

def update_plot(frame):
    if len(time_data) > 0:
        accel_line.set_data(range(len(time_data)), accel_magnitude_data)
        gyro_line.set_data(range(len(time_data)), gyro_magnitude_data)

        # Threshold lines (constant)
        accel_threshold_line.set_data(range(len(time_data)), [ACCEL_VISUAL_THRESHOLD] * len(time_data))
        gyro_threshold_line.set_data(range(len(time_data)), [GYRO_VISUAL_THRESHOLD] * len(time_data))

        # Update x-axis limits dynamically
        ax.set_xlim(max(0, len(time_data) - 100), len(time_data))

        # Adjust y-axis dynamically to include both accel and gyro data
        y_min = min(min(accel_magnitude_data[-100:]), min(gyro_magnitude_data[-100:])) - 0.5
        y_max = max(max(accel_magnitude_data[-100:]), max(gyro_magnitude_data[-100:])) + 0.5
        ax.set_ylim(y_min, y_max)

        # Update fall detection text
        if fall_detected:
            fall_detected_text.set_text('Fall Detected!')
        else:
            fall_detected_text.set_text('No Fall')

    return accel_line, gyro_line, accel_threshold_line, gyro_threshold_line, fall_detected_text

# Start threads for data reading and animation
threading.Thread(target=read_serial_data, daemon=True).start()
ani = animation.FuncAnimation(fig, update_plot, init_func=init, interval=100)
plt.show()
