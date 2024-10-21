import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np
import time

# ---------------------- Variable Zone 1: Step Counting ---------------------- #
SERIAL_PORT = 'COM3'  # Adjust to your COM port
BAUD_RATE = 115200

# Parameters for step detection
STEP_THRESHOLD = 0.4
PEAK_HEIGHT_THRESHOLD = 0.4
MIN_TIME_BETWEEN_STEPS = 300
MAX_SPIKES_WINDOW = 400
STATIONARY_THRESHOLD = 0.05

# Threshold for plot visualization
THRESHOLD_GAP = 3
LOWER_THRESHOLD_GAP = 2

# ---------------------- Variable Zone 2: Fall Detection ---------------------- #
# Parameters for fall detection
ACCEL_FALL_THRESHOLD = 2.5  # Lowered acceleration threshold to 2.5g
GYRO_FALL_THRESHOLD = 2.0   # Lowered gyroscope threshold to 2 degrees/sec
FALL_SUDDEN_CHANGE_THRESHOLD = 1.5  # Sudden change threshold for both acceleration and gyro
STATIONARY_AFTER_FALL = 0.2  # Threshold for being stationary after fall
FALL_STATIONARY_DURATION = 500  # Minimum time to confirm fall stationary

# Filter constants
ACCEL_FILTER_ALPHA = 0.5  # Low-pass filter constant for accelerometer
GYRO_FILTER_ALPHA = 0.5  # Low-pass filter constant for gyroscope

# Data storage
accel_x_data = []
accel_y_data = []
accel_z_data = []
accel_magnitude_data = []
fall_detection_data = []

fall_detected = False
fall_start_time = 0
baseline_accel_magnitude = 0
baseline_gyro_magnitude = 0

time_data = []
gyro_magnitude_data = []
sma_data = []

step_count = 0
last_step_time = 0
crossed_upper_threshold = False
spike_count = 0
last_spike_time = 0
step_detection_paused_until = 0

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Low-pass filter function
def low_pass_filter(value, prev_value, alpha):
    return alpha * value + (1 - alpha) * prev_value

# Function to gather baseline data for calibration
def calibrate_sensors():
    global baseline_accel_magnitude, baseline_gyro_magnitude
    accel_samples = []
    gyro_samples = []
    
    print("Calibrating sensors... Please hold the device still for 3 seconds.")
    
    start_time = time.time()
    while time.time() - start_time < 3:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            try:
                data = line.split(',')
                if len(data) < 7:
                    continue
                # Extract gyro and accel data
                gyro_x = float(data[1].split(':')[-1].strip())
                gyro_y = float(data[2].split(':')[-1].strip())
                gyro_z = float(data[3].split(':')[-1].strip())
                accel_x = float(data[4].split(':')[-1].strip())
                accel_y = float(data[5].split(':')[-1].strip())
                accel_z = float(data[6].split(':')[-1].strip())
                
                # Compute magnitudes
                gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)
                accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
                
                accel_samples.append(accel_magnitude)
                gyro_samples.append(gyro_magnitude)
            except:
                continue
    
    # Calculate average values for baseline
    baseline_accel_magnitude = np.mean(accel_samples)
    baseline_gyro_magnitude = np.mean(gyro_samples)
    print(f"Calibration complete. Baseline acceleration: {baseline_accel_magnitude:.2f}g, Baseline gyroscope: {baseline_gyro_magnitude:.2f}°/s")

# Function to read serial data
def read_serial_data():
    global step_count, last_step_time, crossed_upper_threshold, spike_count
    global last_spike_time, step_detection_paused_until
    global fall_detected, fall_start_time, baseline_accel_magnitude, baseline_gyro_magnitude

    prev_accel_magnitude = baseline_accel_magnitude
    prev_gyro_magnitude = baseline_gyro_magnitude

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            try:
                data = line.split(',')

                if len(data) < 7:
                    print(f"Skipping malformed line: {line}")
                    continue

                # Extract gyroscope and accelerometer data
                gyro_x = float(data[1].split(':')[-1].strip())
                gyro_y = float(data[2].split(':')[-1].strip())
                gyro_z = float(data[3].split(':')[-1].strip())

                accel_x = float(data[4].split(':')[-1].strip())
                accel_y = float(data[5].split(':')[-1].strip())
                accel_z = float(data[6].split(':')[-1].strip())

                # Compute the magnitudes
                gyro_magnitude = np.sqrt(gyro_x**2 + gyro_y**2 + gyro_z**2)
                accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

                # Apply low-pass filter to smooth out noise
                accel_magnitude = low_pass_filter(accel_magnitude, prev_accel_magnitude, ACCEL_FILTER_ALPHA)
                gyro_magnitude = low_pass_filter(gyro_magnitude, prev_gyro_magnitude, GYRO_FILTER_ALPHA)
                prev_accel_magnitude = accel_magnitude
                prev_gyro_magnitude = gyro_magnitude

                current_time = time.time() * 1000  # Get time in milliseconds
                time_data.append(current_time)
                gyro_magnitude_data.append(gyro_magnitude)

                accel_x_data.append(accel_x)
                accel_y_data.append(accel_y)
                accel_z_data.append(accel_magnitude)
                accel_magnitude_data.append(accel_magnitude)

                # Step Counting Logic (Same as Before)
                if len(gyro_magnitude_data) >= 20:
                    sma = np.mean(gyro_magnitude_data[-20:])
                    sma_data.append(sma)
                else:
                    sma_data.append(gyro_magnitude)

                if len(sma_data) > 0:
                    upper_threshold = sma_data[-1] + THRESHOLD_GAP
                    lower_threshold = sma_data[-1] - LOWER_THRESHOLD_GAP

                    if current_time < step_detection_paused_until:
                        continue

                    if gyro_magnitude > upper_threshold and not crossed_upper_threshold:
                        crossed_upper_threshold = True
                        spike_count += 1
                        last_spike_time = current_time

                    elif gyro_magnitude < lower_threshold and crossed_upper_threshold:
                        time_since_last_spike = current_time - last_spike_time
                        if time_since_last_spike < MAX_SPIKES_WINDOW and spike_count >= 2:
                            step_count += 1
                            print(f"Steps detected: {step_count}")
                            last_step_time = current_time
                            step_detection_paused_until = current_time + MIN_TIME_BETWEEN_STEPS
                            spike_count = 0

                        crossed_upper_threshold = False

                    if abs(gyro_magnitude) < STATIONARY_THRESHOLD:
                        crossed_upper_threshold = False

                # --------- Fall Detection Logic --------- #
                accel_change = abs(accel_magnitude - baseline_accel_magnitude)
                gyro_change = abs(gyro_magnitude - baseline_gyro_magnitude)

                if accel_change > FALL_SUDDEN_CHANGE_THRESHOLD and gyro_change > FALL_SUDDEN_CHANGE_THRESHOLD:
                    fall_start_time = current_time
                    fall_detected = True
                    print("Fall detected! Sudden change in acceleration and rotation.")
                    fall_detection_data.append(1)
                else:
                    fall_detection_data.append(0)

            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line}, skipping... {e}")

# Plotting Logic
plt.style.use('fivethirtyeight')
fig, (ax1, ax2) = plt.subplots(2, 1)

line1, = ax1.plot([], [], label='Gyroscope Magnitude', color='blue', linewidth=1)
sma_line, = ax1.plot([], [], label='SMA', color='orange', linewidth=1)
upper_threshold_line, = ax1.plot([], [], color='red', linestyle='-', linewidth=1, label='Upper Threshold')
lower_threshold_line, = ax1.plot([], [], color='green', linestyle='-', linewidth=1, label='Lower Threshold')
step_count_text = ax1.text(0.01, 0.95, '', transform=ax1.transAxes, fontsize=14, verticalalignment='top')

accel_line, = ax2.plot([], [], label='Acceleration Magnitude', color='blue', linewidth=1)
fall_marker, = ax2.plot([], [], 'ro', label='Fall Detected')

def init():
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 5)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Gyro Magnitude')
    ax1.legend()

    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 5)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Accel Magnitude')
    ax2.legend()

    return line1, sma_line, upper_threshold_line, lower_threshold_line, step_count_text, accel_line, fall_marker

def update_plot(frame):
    if len(time_data) > 0:
        line1.set_data(range(len(time_data)), gyro_magnitude_data)
        sma_line.set_data(range(len(time_data)), sma_data)
        upper_threshold_line.set_data(range(len(time_data)), [sma_data[-1] + THRESHOLD_GAP] * len(time_data))
        lower_threshold_line.set_data(range(len(time_data)), [sma_data[-1] - LOWER_THRESHOLD_GAP] * len(time_data))
        ax1.set_xlim(max(0, len(time_data) - 100), len(time_data))
        ax1.set_ylim(min(gyro_magnitude_data[-100:]), max(gyro_magnitude_data[-100:]))
        step_count_text.set_text(f'Steps: {step_count}')

    if len(accel_magnitude_data) > 0:
        accel_line.set_data(range(len(accel_magnitude_data)), accel_magnitude_data)
        fall_x = [i for i, val in enumerate(fall_detection_data) if val == 1]
        fall_y = [accel_magnitude_data[i] for i in fall_x]
        fall_marker.set_data(fall_x, fall_y)
        ax2.set_xlim(max(0, len(accel_magnitude_data) - 100), len(accel_magnitude_data))
        ax2.set_ylim(min(accel_magnitude_data[-100:]), max(accel_magnitude_data[-100:]) + 0.1)

    return line1, sma_line, upper_threshold_line, lower_threshold_line, step_count_text, accel_line, fall_marker

# Start threads for data reading and animation
calibrate_sensors()
threading.Thread(target=read_serial_data, daemon=True).start()
ani = animation.FuncAnimation(fig, update_plot, init_func=init, interval=100)
plt.show()
