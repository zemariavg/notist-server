from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    encrypted_note = Column(Text, nullable=False)
    note_tag = Column(Text, nullable=False)
    iv = Column(Text, nullable=False)
    note_title = Column(Text, nullable=False)
    last_modified_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    last_modifier = relationship("User", foreign_keys=[last_modified_by], backref="modified_notes")

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.note_title}, last_modified_by={self.last_modified_by})>"
    