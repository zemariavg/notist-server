import requests
import os
import logging
from flask import Flask, jsonify, request, abort
from dotenv import load_dotenv
from utils.validators import validate_note

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FE_HOST = os.getenv("FE_HOST")
FE_PORT = os.getenv("FE_PORT")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    try:
        response = requests.get(f"{BACKEND_URL}/users/{username}")

        if response.status_code == 404:
            abort(404, description=response.json().get('error', 'User not found'))

        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/note', methods=['POST'])
def backup_note():
    try:
        app.logger.info(f"Received note backup req from client: {request.remote_addr}")
        note = request.json
        validate_note(note)

        response = requests.post(f"{BACKEND_URL}/note", json=note)
        
        if response.status_code != 200:
            app.logger.error(f"Failed to send note to backend. Response: {response.status_code}")
            abort(400, description=response.json().get('error', 'Invalid JSON'))
        
        app.logger.info(f"Sent note from {request.remote_addr} to backend")
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # logging.basicConfig(filename='frontend.log', level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting frontend server")
    app.run(host=FE_HOST, port=FE_PORT)
