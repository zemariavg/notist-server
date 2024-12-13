from flask import Flask, jsonify, abort
from db.connection import get_db_connection
from db.queries import get_user_by_username
from dotenv import load_dotenv
import os

load_dotenv()
BE_HOST = os.getenv("BE_HOST")
BE_PORT = os.getenv("BE_PORT")

app = Flask(__name__)

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    try:
        conn = get_db_connection()
        user = get_user_by_username(conn, username)

        if not user:
            abort(404, description=f"User '{username}' not found")

        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "public_key": user['public_key']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    app.run(host=BE_HOST, port=BE_PORT)
