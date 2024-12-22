import os
import logging
import requests
from dotenv import load_dotenv

from flask import Flask, abort, request, make_response
from flask.typing import AppOrBlueprintKey
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from db.connection import get_db_session
from helpers.note_helper import handle_note_upsert
from db.queries import get_user_by_username
from utils.tls import get_p12_data

load_dotenv()
BE_HOST = os.getenv("BE_HOST")
BE_PORT = os.getenv("BE_PORT")
P12_PATH = os.getenv("P12_PATH")
P12_PWD = os.getenv("P12_PWD")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    app.logger.info(f"Received user info req from client: {request.remote_addr}")
    try:
        with next(get_db_session()) as session:
            user = get_user_by_username(session, username)
            app.logger.info(f"User found: {user}")
            if user is None:
                abort(404, description="User not found")
                
            return make_response({"user": user.__repr__()}, 200)
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)

@app.route('/note', methods=['POST'])
def backup_note():
    try:
        app.logger.info(f"Received note backup req from client: {request.remote_addr}")
        
        note_data = request.json
        if not note_data:
            app.logger.error("Invalid input: No JSON data received")
            abort(400, description="Invalid input: No JSON data received")

        with next(get_db_session()) as dbsession:
            try:
                note_id = handle_note_upsert(dbsession, note_data, app.logger)
                dbsession.commit()
            except SQLAlchemyError:
                dbsession.rollback()
                raise

        return make_response({"Note saved successfully": note_id}, 201)

    except HTTPException as e:  # Explicitly handle HTTP exceptions
        app.logger.error(f"HTTP error: {str(e)}")
        return make_response({"error": e.description}, e.code)
        
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return make_response({"error": str(e)}, 500)
        
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return make_response({"error": str(e)}, 500)
        

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

    app.run(host=BE_HOST, port=BE_PORT, ssl_context=ssl_context)
