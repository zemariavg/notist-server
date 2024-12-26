from flask import abort, request
from sqlalchemy.exc import SQLAlchemyError
from db.queries import *

def handle_collaborator_upsert(session: Session, request_data: dict, logger):
    logger.info(f"Handling collaborator upsert: {request_data['collaborator']}")

    user_to_add_id, note_id, note_version = verify_request(session, request_data, logger)
    
    new_note_version = create_new_note_version(session, note_id, request_data['note'])
    logger.info(f"Received note: {request_data['note']}")
    logger.info(f"New note version {new_note_version.id} created successfully")

    # Add collaborator
    add_new_collaborator(
        session,
        note_id,
        user_to_add_id,
        request_data['permission'],
        request_data['note']['ciphered_note_key']
    )
    logger.info(f"User {request_data['collaborator']} added as {request_data['permission']} successfully")


def verify_request(session: Session, request_data: dict, logger):
    collaborator_name = request_data['collaborator']
    note_data = request_data['note']
    permission = request_data['permission']
    
    user_to_add_id = get_user_id_by_username(session, collaborator_name)
    if user_to_add_id is None:
        logger.error("User to add as collaborator was not found")
        abort(404, description="User to add as collaborator was not found")
    
    # TODO: When login is added, check if user is adding himself as collaborator
    # TODO: When login is added, check if user sending request is the owner of the note. Only owners can add collaborators

    note_id = fetch_note_id_by_title(session, note_data['title'])
    if note_id is None:
        logger.error("Note to add collaborator not found")
        abort(404, description="Note to add collaborator not found")
    
    if permission not in ['editor', 'viewer']:
        logger.error("Invalid permission. Collaborator permission must be 'editor' or 'viewer'")
        abort(400, description="Invalid permission. Collaborator permission must be 'editor' or 'viewer")

    # check if already user to add is already editor or viewer
    if check_editor_of_note(session, user_to_add_id, note_id) or check_viewer_of_note(session, user_to_add_id, note_id):
        logger.error("User to add is already an editor or viewer")
        abort(400, description="User to add is already an editor or viewer")
    
    note_version = fetch_latest_note_version_by_note_title(session, note_data['title'])
    if note_version.version >= note_data['version']:
        logger.error("Trying to add a collaborator to an outdated version") 
        abort(400, description="Trying to add a collaborator to an outdated version")

    return user_to_add_id, note_id, note_version


def create_new_note_version(session, note_id, note_data):
    new_note_version = NoteVersion(
        note_id=note_id,
        encrypted_note=note_data['encrypted_note'],
        note_tag=note_data['note_tag'],
        iv=note_data['iv'],
        version=note_data['version']
    )
    session.add(new_note_version)
    session.flush()
    return new_note_version


def add_new_collaborator(session, note_id, user_id, permission, ciphered_note_key):
    new_collaborator = Collaborator(
        note_id=note_id,
        user_id=user_id,
        role=permission,
        note_key=ciphered_note_key
    )
    session.add(new_collaborator)
    session.flush()

