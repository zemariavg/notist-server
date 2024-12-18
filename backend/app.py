import os
import logging
from dotenv import load_dotenv

from flask import Flask, jsonify, abort, request
from flask.typing import AppOrBlueprintKey
from sqlalchemy.exc import SQLAlchemyError

from db.connection import get_db_session
from helpers.note_helper import handle_note_upsert

load_dotenv()
BE_HOST = os.getenv("BE_HOST")
BE_PORT = os.getenv("BE_PORT")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# @app.route('/users/<username>', methods=['GET'])
# def get_user(username):
#     try:
#         with next(get_db_session()) as session:
#             user = get_user_by_username(session, username)
            
#             if user is None:
#                 abort(404, description="User not found")
                
#             return jsonify(user.__repr__()), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/notes', methods=['POST'])
def backup_note():
    try:
        app.logger.info(f"Received note backup req from client: {request.remote_addr}")
        
        note_data = request.json
        if not note_data:
            app.logger.error("Invalid input: No JSON data received")
            abort(400, description="Invalid input: No JSON data received")
        app.logger.info(f"Note data: {note_data}")

        with next(get_db_session()) as session:
            try:
                note_id = handle_note_upsert(session, note_data, app.logger)
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise

        return jsonify({"message": "Note saved successfully", "note_id": note_id}), 201
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        app.logger.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
if __name__ == "__main__":
    # logging.basicConfig(filename='backend.log', level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting backend server")
    app.run(host=BE_HOST, port=BE_PORT)
