from re import A
import requests
import os
import logging
from flask import Flask, jsonify, request, abort, make_response
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from utils.validators import validate_note

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FE_HOST = os.getenv("FE_HOST")
FE_PORT = os.getenv("FE_PORT")
SERVER_TIMEOUT = 10 # seconds

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
        note = request.json
        validate_note(note)
        app.logger.info(f"Received note backup req from client: {note['server_metadata']['req_from']}@{request.remote_addr}")

        response = requests.post(f"{BACKEND_URL}/note", json=note, timeout=SERVER_TIMEOUT)
        
        if response.status_code == 403:
            app.logger.error(f"User not authorized to edit note")
            abort(403, description=response.json().get('error', 'User not authorized to edit note'))
        
        if response.status_code == 400:
            app.logger.error(f"Invalid JSON received/Version is outdated")
            abort(400, description=response.json().get('error', 'Invalid JSON'))
        
        if response.status_code != 201:
            app.logger.error(f"Failed to send note to backend. Response: {response.status_code}")
            abort(400, description=response.json().get('error', 'Invalid JSON'))
        
        app.logger.info(f"Sent note from {request.remote_addr} to backend")
        return make_response(response.json(), response.status_code)
        
    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)
        
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)


if __name__ == "__main__":
    # logging.basicConfig(filename='frontend.log', level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting frontend server")
    app.run(host=FE_HOST, port=FE_PORT)
