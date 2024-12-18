from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.relationships import log
from db.queries import *

def handle_note_upsert(session, note_data, logger):
    logger.info(f"Handling note upsert: {note_data}")
    note = get_note_by_note_title(session, note_data['server_metadata']['title'])
    logger.info(f"Note found: {note}")

    if note:
        is_owner = check_owner_of_note(session, note_data['server_metadata']['req_from'], note.id)
        is_editor = check_editor_of_note(session, note_data['server_metadata']['req_from'], note.id)
        
        if not (is_owner or is_editor):
            logger.error("User not authorized to edit note")
            abort(403, description="User not authorized to edit note") 
            
        update_existing_note(session, note, note_data, logger)
        return note.id
    else:
        return insert_new_note(session, note_data, logger)


def update_existing_note(session, note, note_data, logger):
    logger.info(f"Updating note {note.id}")
    last_modifier = get_user_by_username(session, note_data['server_metadata']['last_modifier'])

    note.encrypted_note = note_data['note']
    note.note_tag = note_data['note_tag']
    note.iv = note_data['iv']
    note.last_modified_by = last_modifier.id


def insert_new_note(session, note_data, logger):
    """Insert a new note into the database."""
    logger.info("Inserting new note")
    last_modifier = get_user_by_username(session, note_data['server_metadata']['last_modifier'])
    user = get_user_by_username(session, note_data['server_metadata']['req_from'])

    new_note = Note(
        encrypted_note=note_data['note'],
        note_tag=note_data['note_tag'],
        iv=note_data['iv'],
        note_title=note_data['server_metadata']['title'],
        last_modified_by=last_modifier.id,
    )
    
    # new note so the user is the owner
    new_collaborator = Collaborator(
        user_id=user.id,
        note_id=new_note.id,
        role = "owner",
        note_key = note_data['note_key']
    )
    
    session.add(new_note)
    session.add(new_collaborator)
    return new_note.id, new_collaborator.id
