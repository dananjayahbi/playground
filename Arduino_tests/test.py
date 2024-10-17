import serial.tools.list_ports

def list_all_ports():
    # List all available ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No COM ports available.")
    else:
        print("Available COM ports:")
        for port in ports:
            print(f"{port.device} - {port.description}")

# Run the function to list all COM ports
list_all_ports()
