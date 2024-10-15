import json
import os
import time

class DBHandler:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.running = False

    def start_updating(self):
        """Start the background updating process."""
        self.running = True
        self._update_json()

    def stop_updating(self):
        """Stop the background updating process."""
        self.running = False

    def _update_json(self):
        """Update the JSON file every 3 seconds if running."""
        while self.running:
            current_time = int(time.time())  # Use current time as key
            new_value = f"value at {current_time}"  # Create a value based on current time

            # Read existing data
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as file:
                    data = json.load(file)
            else:
                data = {}

            # Update the data with the new key-value pair
            data[str(current_time)] = new_value

            # Write updated data back to the JSON file
            with open(self.json_file_path, 'w') as file:
                json.dump(data, file, indent=4)

            time.sleep(3)  # Wait for 3 seconds before updating again

    def get_data(self):
        """Return the contents of the JSON file."""
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        else:
            return {}
