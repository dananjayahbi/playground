import serial
import time

# Set the correct COM port and baud rate
COM_PORT = 'COM3'  # Replace with your ESP32 COM port
BAUD_RATE = 115200  # Match the baud rate used in your ESP32 code

try:
    # Initialize serial connection
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)

    # Give the connection a second to settle
    time.sleep(2)

    # Send a simple command to the ESP32
    ser.write(b'Hello ESP32!\n')  # You can change this message

    # Read the response from the ESP32
    response = ser.readline()  # This will wait for a response

    # Print the raw response
    print("Received raw bytes:", response)

except serial.SerialException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Close the serial connection if it was opened
    if 'ser' in locals() and ser.is_open:
        ser.close()
