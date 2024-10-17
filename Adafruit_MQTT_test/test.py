import sys
from Adafruit_IO import MQTTClient

# Set to your Adafruit IO key and username.
ADAFRUIT_IO_KEY = ''  # Replace with your actual key
ADAFRUIT_IO_USERNAME = ''  # Replace with your actual username

# Callback when the client connects to the server.
def connected(client):
    print('Connected to Adafruit IO! Listening for feed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('step-count')  # Replace with your feed name if needed.

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

# Connect to the Adafruit IO server.
try:
    client.connect()  # Establishes connection without any extra parameters
    print("Successfully connected to Adafruit IO!")
    
    # Start the loop to listen for messages
    client.loop_background()  # Run the loop in the background to listen for incoming messages
    print("Listening for messages...")

    # Keep the program running to maintain the connection
    while True:
        pass  # Just wait indefinitely

except Exception as e:
    print(f'Failed to connect: {e}')
