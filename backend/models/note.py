from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base
from models.note_version import NoteVersion

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_title = Column(Text, nullable=False)

    # Relationship with note versions
    versions = relationship("NoteVersion", back_populates="note")

    # Relationship with collaborators
    collaborators = relationship("Collaborator", back_populates="note")

    def __repr__(self):
        return f"<Note(id={self.id}, note_title={self.note_title})>"
