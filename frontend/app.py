import requests
import os
import logging
from flask import Flask, jsonify, request, abort, make_response
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from utils.validators import validate_note_backup_req, validate_add_collaborator_req
from utils.tls import get_p12_data, delete_temp_files

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FE_HOST = os.getenv("FE_HOST")
FE_PORT = os.getenv("FE_PORT")
SERVER_TIMEOUT = 60 # seconds
P12_PATH = os.getenv("P12_PATH")
P12_PWD = os.getenv("P12_PWD")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    app.logger.info(f"Received user info req from client: {request.remote_addr}")
    try:
        response = session.get(f"{BACKEND_URL}/users/{username}", timeout=SERVER_TIMEOUT)

        if response.status_code == 404:
            abort(404, description=response.json().get('error', 'User not found'))

        return make_response(response.json(), response.status_code)
    except Exception as e:
        return make_response({"error": str(e)}, 500)


@app.route('/users/<username>/notes', methods=['GET'])
def get_user_notes(username):
    app.logger.info(f"Received user notes retrieve req from client: {request.remote_addr}")
    try:
        app.logger.info(f"Fetching notes for user {username}")
        response = session.get(f"{BACKEND_URL}/users/{username}/notes")

        if response.status_code == 404:
            app.logger.error(f"User not found")
            abort(404, description=response.json().get('error', 'User not found'))

        if response.status_code == 200:
            app.logger.info(f"Notes fetched successfully")
            
        return make_response(response.json(), response.status_code) 
    except Exception as e:
        app.logger.error(f"Error fetching notes for user {username}: {e}")
        return make_response({"error": str(e)}, 500)

@app.route('/users/<username>/notes/<note_title>/<version>', methods=['GET'])
def get_user_note_version(username, note_title, version):
    app.logger.info(f"Received user note version retrieve req from client: {request.remote_addr}")
    try:
        app.logger.info(f"Fetching note {note_title} for user {username}")
        response = session.get(f"{BACKEND_URL}/users/{username}/notes/{note_title}/{version}", timeout=SERVER_TIMEOUT)

        if response.status_code == 404:
            app.logger.error(f"Note not found")
            abort(404, description=response.json().get('error', 'Note not found'))

        if response.status_code == 200:
            app.logger.info(f"Note fetched successfully")
            print(response.json())
            
        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error fetching note {note_title} for user {username}: {e}")
        return make_response({"error": str(e)}, 500)
        
@app.route('/users/<username>/pub_key', methods=['GET'])
def get_user_pub_key(username):
    app.logger.info(f"Received user public key req from client: {request.remote_addr}")
    try:
        response = session.get(f"{BACKEND_URL}/users/{username}/pub_key", timeout=SERVER_TIMEOUT)

        if response.status_code == 404:
            app.logger.error(f"User not found")
            abort(404, description=response.json().get('error', 'User not found'))
        app.logger.info(f"User found: {response.json()}")
        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error fetching public key for user {username}: {e}")
        return make_response({"error": str(e)}, 500)
        
@app.route('/add_collaborator', methods=['POST'])
def add_colaborator():
    app.logger.info(f"Received add colaborator req from client: {request.remote_addr}")
    try:
        validate_add_collaborator_req(request.json)
        response = session.post(f"{BACKEND_URL}/add_collaborator", json=request.json, timeout=SERVER_TIMEOUT)
        
        if response.status_code == 404:
            app.logger.error(f"User not found")
            abort(404, description=response.json().get('error', 'User not found'))
        
        if response.status_code == 201:
            app.logger.info(f"User added as collaborator successfully")
            
        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error adding colaborator: {e}")
        return make_response({"error": str(e)}, 500)

@app.route('/backup_note', methods=['POST'])
def backup_note():
    app.logger.info(f"Received note backup req from client: {request.remote_addr}")
    try:
        validate_note_backup_req(request.json)
        app.logger.info(f"note: {request.json}")
        app.logger.info(f"Received note backup req from client: {request.json['req_from']}@{request.remote_addr}")

        response = session.post(f"{BACKEND_URL}/backup_note", json=request.json, timeout=SERVER_TIMEOUT)
        app.logger.info(f"Sent note from {request.remote_addr} to backend")
        
        if response.status_code == 403:
            app.logger.error(f"User not authorized to edit note")
            abort(403, description=response.json().get('error', 'User not authorized to edit note'))

        if response.status_code == 400:
            app.logger.error(f"Invalid JSON received/Version is outdated")
            abort(400, description=response.json().get('error', 'Invalid JSON'))

        if response.status_code != 201:
            app.logger.error(f"Failed to send note to backend. Response: {response.status_code}")
            abort(400, description=response.json().get('error', 'Invalid JSON'))
        
        app.logger.info(f"Note saved successfully")
        return make_response(response.json(), response.status_code)

    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)

    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("frontend.log"),
            logging.StreamHandler()
        ]
    )
    app.logger.info("Starting frontend server")
    
    app.logger.info("Loading server certificates for tls")
    fe_cert, fe_key, be_cert = get_p12_data(P12_PATH, P12_PWD)
    ssl_context = (fe_cert, fe_key)
    session = requests.Session()
    session.cert = (fe_cert, fe_key)
    session.verify = be_cert
    app.logger.info("Certificates loaded successfully")
    
    temp_files = [fe_cert, fe_key, be_cert] 
    
    try:
        app.run(host=FE_HOST, port=FE_PORT, ssl_context=ssl_context)
    finally:
        delete_temp_files(temp_files)  # Cleanup certificates
