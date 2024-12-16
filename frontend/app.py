from flask import Flask, jsonify, request, abort
import requests
from dotenv import load_dotenv
import os

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
        note = request.json
        if note is None or not isinstance(note, dict) or 'server_metadata' not in note:
            abort(400, description="Invalid JSON")        
        
        response = requests.post(f"{BACKEND_URL}/note", json=note)
        
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host=FE_HOST, port=FE_PORT)

