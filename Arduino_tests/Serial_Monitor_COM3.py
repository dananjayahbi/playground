import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set up the serial connection (adjust COM port and baudrate as needed)
SERIAL_PORT = 'COM3'  # Adjust this if your ESP32 is on a different port
BAUD_RATE = 115200  # Should match the baud rate of the ESP32 code
TIMEOUT = 1  # Timeout for reading serial data

# Initialize variables for plotting
step_count = 0
fall_detected = False
step_data = []  # List to store step count history
fall_data = []  # List to store fall detection history
time_data = []  # List to store time history

def read_serial_data():
    global step_count, fall_detected, step_data, fall_data, time_data
    try:
        # Open the serial connection to the ESP32
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for the connection to establish

        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baudrate.")
        print("Listening for step count and fall detection data...\n")

        while True:
            # Read the serial data line by line
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"Received: {line}")
                        # Check if the line contains step count or fall detection
                        if "Step detected!" in line:
                            step_count += 1
                            step_data.append(step_count)
                            fall_data.append(fall_detected)
                            time_data.append(time.time() - start_time)
                        elif "Fall detected!" in line:
                            fall_detected = True
                            step_data.append(step_count)
                            fall_data.append(fall_detected)
                            time_data.append(time.time() - start_time)
                        else:
                            fall_data.append(fall_detected)
                            step_data.append(step_count)
                            time_data.append(time.time() - start_time)

                except UnicodeDecodeError as e:
                    print(f"Decoding error: {e}")

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        print("Stopping serial monitoring.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

def update_plot(frame):
    plt.cla()  # Clear the current axes
    plt.title('Step Count and Fall Detection')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Counts')
    plt.xlim(0, 30)  # Display last 30 seconds of data

    # Plot step count
    if time_data:
        plt.plot(time_data, step_data, label='Step Count', color='blue')
    
    # Plot fall detection
    if fall_data:
        for i in range(len(fall_data)):
            if fall_data[i]:
                plt.axvline(x=time_data[i], color='red', linestyle='--', label='Fall Detected' if i == 0 else "")
    
    plt.legend()
    plt.tight_layout()

# Run the read_serial_data in a separate thread to avoid blocking the plotting
import threading

# Record the start time for x-axis reference
start_time = time.time()

data_thread = threading.Thread(target=read_serial_data)
data_thread.daemon = True  # This thread will exit when the main program exits
data_thread.start()

# Set up the plot
plt.figure(figsize=(10, 5))
ani = FuncAnimation(plt.gcf(), update_plot, interval=1000)  # Update every second
plt.show()
