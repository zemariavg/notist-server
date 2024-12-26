from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from db.queries import *

def handle_note_upsert(session: Session, note_data: dict, logger):
    logger.info(f"Handling note upsert: {note_data}")
    note_id = fetch_note_id_by_title(session, note_data['title'])
    
    logger.info(f"Note found. ID: {note_id}")

    if note_id is not None:
        note = fetch_latest_note_version_by_note_title(session, note_data['title'])
        logger.info(f"Note found. ID: {note.id}")
        
        owner = get_user_by_username(session, note_data['req_from'])
        logger.info(f"Owner found: {owner}")
        
        is_owner = check_owner_of_note(session, owner.id, note_id)
        is_editor = check_editor_of_note(session, owner.id, note_id)
        logger.info(f"Owner: {is_owner}, Editor: {is_editor}")
        
        if not (is_owner or is_editor):
            logger.error("User not authorized to edit note")
            abort(403, description="User not authorized to edit note") 
            
        if note.version >= note_data['version']:
            logger.error("Trying to update with outdated version")
            abort(400, description="Trying to update with outdated version")
        
        newid= update_existing_note(session, note_id, note, note_data, logger)
        return newid
    else:
        return insert_new_note(session, note_data, logger)


def update_existing_note(session: Session, note_id: int, note_version: NoteVersion, note_data: dict, logger):
    logger.info(f"Adding new version {note_data['version']} to note {note_id}")
    
    new_note_version = NoteVersion(
        note_id=note_id,
        encrypted_note=note_data['encrypted_note'],
        note_tag=note_data['note_tag'],
        iv=note_data['iv'],
        version=note_data['version']
    )
    
    session.add(new_note_version)
    session.flush()
    
    return new_note_version.id
    

def insert_new_note(session: Session, note_data: dict, logger):
    """Insert a new note into the database."""
    logger.info("Inserting new note")
    
    owner = get_user_by_username(session, note_data['req_from'])
    
    new_note = Note(note_title=note_data['title'])
    session.add(new_note)
    session.flush()
    
    print(f"new_note.id: {new_note.id}")
    
    new_note_version = NoteVersion(
        note_id=new_note.id,
        encrypted_note=note_data['encrypted_note'],
        note_tag=note_data['note_tag'],
        iv=note_data['iv'],
        version=note_data['version']
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