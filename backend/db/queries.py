from models.user import User
from models.note import Note
from models.note_version import NoteVersion
from models.collaborator import Collaborator
from sqlalchemy.orm.session import Session
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased

def get_user_by_username(session: Session, username: str) -> User:
    return session.query(User).filter(
        User.username == username
    ).first()

def get_user_id_by_username(session: Session, username: str):
    user = get_user_by_username(session, username)
    
    if user is None:
        return None
    
    return user.id

def fetch_note_id_by_title(session: Session, note_title: str):
    note = session.query(Note).filter(Note.note_title == note_title).first()
    
    if note is None:
        return None 
    
    return note.id
    
def fetch_latest_note_version_by_note_title(session: Session, note_title: str) -> NoteVersion:
    return session.query(NoteVersion).join(Note).filter(
        Note.note_title == note_title
    ).order_by(desc(NoteVersion.version)).first() 

def fetch_note_version_by_title_and_version(session: Session, note_title: str, version: int) -> NoteVersion:
    return session.query(NoteVersion).join(Note).filter(
        Note.note_title == note_title,
        NoteVersion.version == version
    ).first()

def fetch_notes_for_user(session: Session, user_id: int):
    latest_version_subquery = (
        session.query(
            NoteVersion.note_id.label("note_id"),
            func.max(NoteVersion.version).label("latest_version")
        )
        .group_by(NoteVersion.note_id)
        .subquery()
    )

    results = (
        session.query(
            Note.note_title,
            NoteVersion.iv,
            NoteVersion.encrypted_note,
            NoteVersion.note_tag,
            Collaborator.note_key,
            Collaborator.role
        )
        .join(Collaborator, Collaborator.note_id == Note.id)  # Join with collaborators
        .join(latest_version_subquery, latest_version_subquery.c.note_id == Note.id)  # Join with subquery
        .join(
            NoteVersion,
            (NoteVersion.note_id == latest_version_subquery.c.note_id) &
            (NoteVersion.version == latest_version_subquery.c.latest_version)  # Match latest version
        )
        .filter(Collaborator.user_id == user_id)  # Filter by user ID
        .all()
    )

    notes = {"owner": [], "editor": [], "viewer": []}
       
    for note_title, iv, encrypted_note, note_tag, note_key, role in results:
        note_dict = {
            "title": note_title,
            "iv": iv,
            "encrypted_note": encrypted_note,
            "note_tag": note_tag,
            "ciphered_note_key": note_key
        }
        notes[role].append(note_dict)
        
    return notes
    
def check_editor_of_note(session: Session, user_id: int, note_id: int) -> bool:
    return session.query(Collaborator).filter(
        Collaborator.user_id == user_id, 
        Collaborator.note_id == note_id, 
        Collaborator.role == 'editor'
    ).first() is not None

def check_viewer_of_note(session: Session, user_id: int, note_id: int) -> bool:
    return session.query(Collaborator).filter(
        Collaborator.user_id == user_id, 
        Collaborator.note_id == note_id, 
        Collaborator.role == 'viewer'
    ).first() is not None

def check_owner_of_note(session: Session, user_id: int, note_id: int) -> bool:
    return session.query(Collaborator).filter(
        Collaborator.user_id == user_id, 
        Collaborator.note_id == note_id, 
        Collaborator.role == 'owner'
    ).first() is not None

