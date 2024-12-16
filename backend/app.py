import os
import logging
from flask import Flask, jsonify, abort, request
from db.connection import get_db_session
from db.queries import get_user_by_username
from models.note import Note
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()
BE_HOST = os.getenv("BE_HOST")
BE_PORT = os.getenv("BE_PORT")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    try:
        with next(get_db_session()) as session:
            user = get_user_by_username(session, username)
            
            if user is None:
                abort(404, description="User not found")
                
            return jsonify(user.__repr__()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/note', methods=['POST'])
def backup_note():
    try:
        app.logger.info(f"Received note backup req from client: {request.remote_addr}")
        note_data = request.json
        if not note_data:
            app.logger.error("Invalid input: No JSON data received")
            abort(400, description="Invalid input: No JSON data received")

        app.logger.info(f"note data: {note_data}")

        with next(get_db_session()) as session:
            user_owner = get_user_by_username(session, note_data['server_metadata']['owner'])
            user_last_modifier = get_user_by_username(session, note_data['server_metadata']['last_modified_by'])

            if user_owner is None or user_last_modifier is None:
                app.logger.error(f"User not found: {'owner' if user_owner is None else 'last modifier'}")
                abort(404, description="User not found")

            new_note = Note(
                encrypted_note=note_data['note'],
                note_tag=note_data['note_tag'],
                iv=note_data['iv'],
                owner_id=user_owner.id,
                last_modified_by=user_last_modifier.id,
                owner_note_key=note_data['note_key']
            )
            
            # TODO: IMPORTANT check if note already exists (by name or hash?)
            session.add(new_note)
            session.commit()

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
