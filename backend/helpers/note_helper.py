from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from db.queries import *

def handle_note_upsert(session: Session, note_data: dict, headers: dict, logger):
    logger.info(f"Handling note upsert: {note_data}")
    note_id = fetch_note_id_by_title(session, note_data['title'])

    if note_id is not None:
        note = fetch_latest_note_version_by_note_title(session, note_data['title'])
        logger.info(f"Note found. is: {note.id}")
        owner = get_user_by_username(session, headers['req_from'])
        logger.info(f"Owner found: {owner}")
        is_owner = check_owner_of_note(session, owner.id, note_id)
        is_editor = check_editor_of_note(session, owner.id, note_id)
        logger.info(f"Owner: {is_owner}, Editor: {is_editor}")
        
        if not (is_owner or is_editor):
            logger.error("User has no write permissions")
            abort(403, description="User has no write permissions") 

        if int(headers['version']) < note.version:
            logger.error("Trying to update with outdated version")
            abort(405, description="Trying to update with outdated version")
        elif int(headers['version']) == note.version:
            return note_id

        newid = update_existing_note(session, note_id, note_data, headers, logger)
        return newid
    else:
        abort(402, description="Note does not exist in the database")


def update_existing_note(session: Session, note_id: int, note_data: dict, headers: dict, logger):
    logger.info(f"Adding new version {headers['version']} to note {note_id}")
    
    new_note_version = NoteVersion(
        note_id=note_id,
        iv=note_data['iv'],
        encrypted_note=note_data['encrypted_note'],
        note_tag=note_data['note_tag'],
        version=int(headers['version'])
    )
    
    session.add(new_note_version)
    session.flush()
    
    return new_note_version.id
    

def insert_new_note(session: Session, note_data: dict, headers: dict, logger):
    """Insert a new note into the database."""
    logger.info("Inserting new note")
    note_id = fetch_note_id_by_title(session, note_data['title'])

    if note_id is not None:
        logger.error(f"Note already exists in the database")
        abort(401, description="Note already exists in the database")

    owner = get_user_by_username(session, headers['req_from'])
    
    new_note = Note(note_title=note_data['title'])
    session.add(new_note)
    session.flush()
    
    print(f"new_note.id: {new_note.id}")
    
    new_note_version = NoteVersion(
        note_id=new_note.id,
        iv=note_data['iv'],
        encrypted_note=note_data['encrypted_note'],
        note_tag=note_data['note_tag'],
        version=1
    )
    
    session.add(new_note_version)
    session.flush()

    new_collaborator = Collaborator(
        user_id=owner.id,
        note_id=new_note.id,
        role="owner",
        note_key=note_data['ciphered_note_key']
    )
    session.add(new_collaborator)
    return new_note_version.id