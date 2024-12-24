from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from db.connection import Base

class NoteVersion(Base):
    __tablename__ = 'note_versions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey('notes.id'), nullable=False)
    version = Column(Integer, nullable=False)
    encrypted_note = Column(Text, nullable=False)
    iv = Column(Text, nullable=False)
    note_tag = Column(Text, nullable=False)

    note = relationship("Note", back_populates="versions")

    def __repr__(self):
        return f"<NoteVersion(id={self.id}, note_id={self.note_id}, version={self.version}, note_tag={self.note_tag})>"