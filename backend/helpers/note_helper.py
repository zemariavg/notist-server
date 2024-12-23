from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.relationships import log
from db.queries import *

def handle_note_upsert(session, note_data, logger):
    logger.info(f"Handling note upsert: {note_data}")
    note = fetch_note_by_note_title(session, note_data['title'])
    logger.info(f"Note found: {note}")

    if note:
        owner = get_user_by_username(session, note_data['req_from'])
        is_owner = check_owner_of_note(session, owner.id, note.id)
        is_editor = check_editor_of_note(session, owner.id, note.id)
        
        if not (is_owner or is_editor):
            print(f"owner: {is_owner}, editor: {is_editor}")
            logger.error("User not authorized to edit note")
            abort(403, description="User not authorized to edit note") 
            
        if note.version >= note_data['version']:
            logger.error("Trying to update with outdated version")
            abort(400, description="Trying to update with outdated version")
        
        update_existing_note(session, note, note_data, logger)
        return note.id
    else:
        return insert_new_note(session, note_data, logger)


def update_existing_note(session, note, note_data, logger):
    logger.info(f"Updating note {note.id}")

    note.encrypted_note = note_data['encrypted_note']
    note.note_tag = note_data['note_tag']
    note.iv = note_data['iv']
    note.version = note_data['version']


def insert_new_note(session, note_data, logger):
    """Insert a new note into the database."""
    logger.info("Inserting new note")
    
    owner = get_user_by_username(session, note_data['req_from'])
    
    new_note = Note(note_title=note_data['title'])
    session.add(new_note)
    session.flush()
    
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
        note_key=note_data['note_key']
    )
    session.add(new_collaborator)
    return new_note.id