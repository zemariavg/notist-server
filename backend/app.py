import os
import logging
import requests
from dotenv import load_dotenv

from flask import Flask, abort, current_app, request, make_response, jsonify
from flask.typing import AppOrBlueprintKey
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from db.queries import *
from db.connection import get_db_session
from helpers.note_helper import handle_note_upsert
from helpers.collaborator_helper import handle_collaborator_upsert
from utils.tls import get_p12_data, delete_temp_files
from helpers.note_helper import handle_note_upsert, insert_new_note
from utils.tls import get_p12_data
#from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

load_dotenv()
BE_HOST = os.getenv("BE_HOST")
BE_PORT = os.getenv("BE_PORT")
P12_PATH = os.getenv("P12_PATH")
P12_PWD = os.getenv("P12_PWD")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

"""
def verify_password(user, password):
    #return bcrypt.check_password_hash(user.password_hash, password)
"""

@app.route('/login', methods=['POST'])
def login():
    app.logger.info(f"Received login req from client: {request.remote_addr}")
    try:
        with next(get_db_session()) as session:
            data = request.get_json()
            
            user = get_user_by_username(session, data['username'])
            app.logger.info(f"Logging in user {data['username']}")

            if not user or not user.password_hash == data['password']:
                app.logger.error("Invalid credentials")
                return jsonify({'message': 'Invalid credentials'}), 406

            # Create JWT token
            app.logger.info("User authenticated")
            token = create_access_token(identity=user.username)
            
            app.logger.info(f"Token generated: {token}")
            return jsonify({'token': token}), 200
    except Exception as e:
        app.logger.error(f"login: {str(e)}")
        return make_response("Internal Server Error", 500)

@app.route('/users/<username>/notes', methods=['GET'])
def get_user_notes(username):
    app.logger.info(f"Received user notes retrieve req from client: {request.remote_addr}")
    
    try:
        with next(get_db_session()) as session:
            user = get_user_by_username(session, username)
            if not user:
                abort(404, description="User not found")
                
            user_notes = fetch_notes_for_user(session, user.id)
            app.logger.info(f"Notes fetched for user {username}: {user_notes}")
            app.logger.info(f"Notes fetched successfully")
            return jsonify(user_notes), 200
    except Exception as e:
        app.logger.error(f"get_user_notes: Error fetching notes for user {username}: {e}")
        return make_response("Internal Server Error", 500)

@app.route('/users/<username>/pub_key', methods=['GET'])
def get_user_pub_key(username):
    app.logger.info(f"Received user public key req from client: {request.remote_addr}")
    try:
        with next(get_db_session()) as session:
            user = get_user_by_username(session, username)
            if not user:
                abort(404, description="User not found")
                
            app.logger.info(f"User found: {user}")
            return make_response({"pub_key": user.public_key}, 200)
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)

@app.route('/users/<username>/notes/<note_title>/<version>', methods=['GET'])
def get_user_note_version(username, note_title, version):
    app.logger.info(f"Received user note version retrieve req from client: {username}@{request.remote_addr}")
    try:
        with next(get_db_session()) as session:
            user = get_user_by_username(session, username)
            if not user:
                abort(404, description="User not found")
                
            note = fetch_specific_note_version(session, user.id, note_title, version)
            if not note:
                abort(404, description="Note not found")
                
            app.logger.info(f"Note fetched successfully")
            return jsonify(note), 200
    except Exception as e:
        app.logger.error(f"Error fetching note {note_title} for user {username}: {e}")
        return make_response({"error": str(e)}, 500)
    
@app.route('/users/<username>/add_collaborator', methods=['POST'])
def add_collaborator(username):
    app.logger.info(f"Received add collaborator req from client: {username}@{request.remote_addr}")
    try:
        if request.json is None:
            app.logger.error("Invalid input: No JSON data received")
            abort(400, description="Invalid input: No JSON data received")
         
        with next(get_db_session()) as dbsession:
            try:
                handle_collaborator_upsert(dbsession, username, request.json, app.logger)
                dbsession.commit()
            except SQLAlchemyError:
                app.logger.error("An error occurred, rolling back changes.")
                dbsession.rollback()
                raise
        
        return make_response({"message": "Collaborator added successfully"}, 201)
    
    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)
    
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response("Internal server error", 500) 
    

@app.route('/users/<username>/backup_note', methods=['POST'])
def backup_note(username):
    app.logger.info(f"Received note backup req from client: {username}@{request.remote_addr}")
    try:

        note_data = request.json

        if not note_data:
            app.logger.error("Invalid input: No JSON data received")
            abort(400, description="Invalid input: No JSON data received")

        with next(get_db_session()) as dbsession:
            try:
                note_id = handle_note_upsert(dbsession, note_data, username, request.headers, app.logger)
                dbsession.commit()
            except SQLAlchemyError:
                app.logger.error("An error occurred, rolling back changes.")
                dbsession.rollback()
                raise

        return make_response({"Note saved successfully": note_id}, 201)

    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)

    except Exception as e:
        app.logger.error(f"backup_note: Internal server error: {str(e)}")
        return make_response("Internal Server Error", 500)

@app.route('/users/<username>/create_note', methods=['POST'])
def create_note(username):
    try:
        app.logger.info(f"Received create note req from client: {username}@{request.remote_addr}")

        note_data = request.json

        if not note_data:
            app.logger.error("Invalid input: No JSON data received")
            abort(405, description="Invalid input: No JSON data received")

        with next(get_db_session()) as dbsession:
            try:
                note_id = insert_new_note(dbsession, note_data, username, app.logger)
                dbsession.commit()
            except SQLAlchemyError:
                dbsession.rollback()
                raise

        return make_response({"Note created successfully": note_id}, 201)

    except HTTPException as e:
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)

    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response("Internal server error", 500)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("backend.log"),
            logging.StreamHandler()
        ]
    )
    app.logger.info("Starting backend server")
    
    app.logger.info("Loading server certificates for tls")
    be_cert, be_key, fe_cert = get_p12_data(P12_PATH, P12_PWD)
    ssl_context = (be_cert, be_key)
    session = requests.Session()
    session.cert = (be_cert, be_key)
    session.verify = fe_cert
    app.logger.info("Certificates loaded successfully")

    temp_files = [be_cert, be_key, fe_cert] 
    
    try:
        app.run(host=BE_HOST, port=BE_PORT, ssl_context=ssl_context)
    finally:
        delete_temp_files(temp_files)  # Cleanup certificates
