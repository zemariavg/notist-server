import requests
import os
import logging
from flask import Flask, current_app, jsonify, request, abort, make_response
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from utils.validators import validate_add_collaborator_req, validate_note, check_version
from utils.tls import get_p12_data, delete_temp_files
from flask_jwt_extended import current_user, jwt_required, JWTManager, get_jwt_identity
from utils.errors import validate_response
import jwt

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FE_HOST = os.getenv("FE_HOST")
FE_PORT = os.getenv("FE_PORT")
SERVER_TIMEOUT = 60 # seconds
P12_PATH = os.getenv("P12_PATH")
P12_PWD = os.getenv("P12_PWD")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwtmanager = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    app.logger.info(f"Received login req from client: {request.remote_addr}")
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            app.logger.error("Username and password are required")
            return jsonify({'message': 'Username and password are required!'}), 400

        app.logger.info(f"Logging in user {data['username']}")
        response = session.post(f"{BACKEND_URL}/login", json=data, timeout=SERVER_TIMEOUT)

        if response.status_code == 406:
            app.logger.error("Invalid credentials")
            return jsonify({'message': 'Invalid credentials'}), 406

        if response.status_code == 200:
            app.logger.info("User authenticated")
            return make_response(response.json(), response.status_code)

        return make_response(response.json(), response.status_code)

    except Exception as e:
        app.logger.error(f"login: {str(e)}")
        return make_response("Internal Server Error", 500)

@app.route('/users/<username>/notes', methods=['GET'])
@jwt_required()
def get_user_notes(username):
    app.logger.info(f"Received user notes retrieve req from client: {request.remote_addr}")

    try:
        app.logger.info(f"Fetching notes for user {username}")
        response = session.get(f"{BACKEND_URL}/users/{username}/notes", headers=request.headers)

        validate_response(app, response)

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

        validate_response(app, response)

        if response.status_code == 200:
            app.logger.info(f"Note fetched successfully")
            print(response.json())

        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error fetching note {note_title} for user {username}: {e}")
        return make_response({"error": str(e)}, 500)

@app.route('/users/<username>/pub_key', methods=['GET'])
@jwt_required()
def get_user_pub_key(username):
    app.logger.info(f"Received user public key req from client: {request.remote_addr}")
    try:
        response = session.get(f"{BACKEND_URL}/users/{username}/pub_key", timeout=SERVER_TIMEOUT)

        validate_response(app, response)

        app.logger.info(f"User found: {response.json()}")
        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error fetching public key for user {username}: {e}")
        return make_response({"error": str(e)}, 500)

@app.route('/add_collaborator', methods=['POST'])
@jwt_required()
def add_colaborator():
    app.logger.info(f"Received add colaborator req from client: {request.remote_addr}")
    current_user = get_jwt_identity()
    app.logger.info(f"Current user: {current_user}")

    try:
        validate_add_collaborator_req(request.json)
        response = session.post(f"{BACKEND_URL}/users/{current_user}/add_collaborator", json=request.json, timeout=SERVER_TIMEOUT)

        validate_response(app, response)

        if response.status_code == 201:
            app.logger.info(f"User added as collaborator successfully")

        return make_response(response.json(), response.status_code)
    except Exception as e:
        app.logger.error(f"Error adding colaborator: {e}")
        return make_response({"error": str(e)}, 500)

@app.route('/backup_note', methods=['POST'])
@jwt_required()
def backup_note():
    app.logger.info(f"Received note backup req from client: {request.remote_addr}")
    current_user = get_jwt_identity()
    app.logger.info(f"Current user: {current_user}")
    
    try:
        note = request.json
        validate_note(note, request.headers)

        app.logger.info(f"Received note backup req from client: {current_user}@{request.remote_addr}")

        response = session.post(f"{BACKEND_URL}/users/{current_user}/backup_note", json=note, timeout=SERVER_TIMEOUT, headers=request.headers)
        app.logger.info(f"Sent note from {request.remote_addr} to backend")

        validate_response(app, response)
        
        app.logger.info(f"Note saved successfully")
        return make_response(response.json(), response.status_code)

    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)

    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)


@app.route('/create_note', methods=['POST'])
@jwt_required()
def create_note():
    app.logger.info(f"Received create note req from client: {request.remote_addr}")
    current_user = get_jwt_identity()
    app.logger.info(f"Current user: {current_user}")
    
    try:
        note = request.json
        headers = request.headers
        validate_note(note, headers)
        check_version(headers)
        app.logger.info(f"note: {note}")

        response = session.post(f"{BACKEND_URL}/users/{current_user}/create_note", json=note, timeout=SERVER_TIMEOUT, headers=headers)
        app.logger.info(f"Sent note from {request.remote_addr} to backend")

        validate_response(app, response)

        app.logger.info(f"Note created successfully")
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
