from models.user import User
from models.note import Note
from models.collaborator import Collaborator
from sqlalchemy.orm.session import Session

def get_user_by_username(session: Session, username: str) -> User:
    return session.query(User).filter(
        User.username == username
    ).first()

def get_note_by_note_title(session: Session, note_title: str) -> Note:
    return session.query(Note).filter(
        Note.note_title == note_title
    ).first()

def get_view_notes(session: Session, user_id: int):
    return session.query(Note).join(Collaborator).filter(
        Collaborator.user_id == user_id,
        Collaborator.role == "viewer"
    ).all()

def get_edit_notes(session: Session, user_id: int):
    return session.query(Note).join(Collaborator).filter(
        Collaborator.user_id == user_id,
        Collaborator.role == "editor"
    ).all()

def get_own_notes(session: Session, user_id: int):
    return session.query(Note).join(Collaborator).filter(
        Collaborator.user_id == user_id,
        Collaborator.role == "owner"
    ).all()

def get_notes_by_user_id(session: Session, user_id: int) -> dict:
    own_notes = get_own_notes(session, user_id)
    edit_notes = get_edit_notes(session, user_id)
    view_notes = get_view_notes(session, user_id)
    return {
        "owner": [note.to_dict() for note in own_notes],
        "editor": [note.to_dict() for note in edit_notes],
        "viewer": [note.to_dict() for note in view_notes],
    }

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

