from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.connection import Base

class Collaborator(Base):
    __tablename__ = "collaborators"

    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    role = Column(String(50), nullable=False)
    note_key = Column(Text, nullable=False)

    note = relationship("Note", backref="collaborators")
    user = relationship("User", backref="collaborations")

    def __repr__(self):
        return f"<Collaborator(note_id={self.note_id}, user_id={self.user_id}, role={self.role})>"
