from flask import Flask, current_app, jsonify, request, abort, make_response


def validate_response(app, response):
    if response.status_code == 401:
        app.logger.error(f"Note already exists in the database")
        abort(401, description=response.json().get('error', 'Note already exists in the database'))

    if response.status_code == 402:
        app.logger.error(f"Note does not exist in the database")
        abort(402, description=response.json().get('error', 'Note does not exist in the database'))

    if response.status_code == 403:
        app.logger.error(f"User has no write permissions")
        abort(403, description=response.json().get('error', 'User has no write permissions'))

    if response.status_code == 404:
        app.logger.error(f"User not found")
        abort(404, description=response.json().get('error', 'User not found'))

    if response.status_code == 405:
        app.logger.error(f"Invalid JSON received / Version is outdated")
        abort(405, description=response.json().get('error', 'Invalid JSON received / Version is outdated'))

    if response.status_code > 201:
        app.logger.error(f"Failed to send note to backend. Response: {response.status_code}")
        abort(500, description=response.json().get('error', 'Failed to send note to backend.'))

