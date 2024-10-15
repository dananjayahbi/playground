from flask import Blueprint, request, jsonify
from dbHandler import DBHandler

# Initialize a Blueprint for routes
routes = Blueprint('routes', __name__)

# Create an instance of the DBHandler
db_handler = DBHandler('data.json')

# Route to start or stop the updating process
@routes.route('/process', methods=['POST'])
def control_process():
    data = request.get_json()
    
    if not data or 'action' not in data:
        return jsonify({"error": "Invalid request. Please provide 'action'."}), 400

    action = data['action'].lower()

    if action == 'start':
        if not db_handler.running:
            db_handler.start_updating()
            return jsonify({"message": "Data writing process started."}), 200
        else:
            return jsonify({"message": "Data writing process is already running."}), 200

    elif action == 'stop':
        if db_handler.running:
            db_handler.stop_updating()
            return jsonify({"message": "Data writing process stopped."}), 200
        else:
            return jsonify({"message": "Data writing process is not running."}), 200

    else:
        return jsonify({"error": "Invalid action. Use 'start' or 'stop'."}), 400

# Route to get the current data in the JSON file
@routes.route('/data', methods=['GET'])
def get_data():
    data = db_handler.get_data()
    return jsonify(data), 200


# A test route
@routes.route('/')
def hello():
    return "Hello, World!"