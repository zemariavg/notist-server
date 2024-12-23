from models.user import User
from models.note import Note
from models.note_version import NoteVersion
from models.collaborator import Collaborator
from sqlalchemy.orm.session import Session
from sqlalchemy import desc

def get_user_by_username(session: Session, username: str) -> User:
    return session.query(User).filter(
        User.username == username
    ).first()

def fetch_note_by_note_title(session: Session, note_title: str) -> NoteVersion:
    return session.query(NoteVersion).join(Note).filter(
        Note.note_title == note_title
    ).order_by(desc(NoteVersion.version)).first() 

def fetch_note_by_title_and_version(session: Session, note_title: str, version: int) -> NoteVersion:
    return session.query(NoteVersion).join(Note).filter(
        Note.note_title == note_title,
        NoteVersion.version == version
    ).first()

def fetch_notes_for_user(session: Session, user_id: int):
    # Get all notes the user has access to (either as owner, editor, or viewer)
    results = session.query(
        Note.note_title,
        NoteVersion.iv,
        NoteVersion.encrypted_note,
        NoteVersion.note_tag,
        Collaborator.note_key
    ).join(Collaborator, Collaborator.note_id == Note.id)\
    .join(NoteVersion, NoteVersion.note_id == Note.id)\
    .filter(Collaborator.user_id == user_id)\
    .order_by(NoteVersion.version.desc())\
    .distinct(Note.id)\
    .all()

    notes = [
        {
            "title": note_title,
            "iv": iv,
            "note": encrypted_note,
            "note_tag": note_tag,
            "note_key": note_key
        }
        for note_title, iv, encrypted_note, note_tag, note_key in results
    ]
    
    if not notes:
        return {"editor": [], "viewer": [], "owner": []}
    
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

