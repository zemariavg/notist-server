from .connection import get_db_session
from models.user import User
from sqlalchemy.orm.session import Session

def get_user_by_username(session: Session, username: str) -> User:
    return session.query(User).filter(User.username == username).first()