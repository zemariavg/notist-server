from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base

class Collaborator(Base):
    __tablename__ = 'collaborators'

    note_id = Column(Integer, ForeignKey('notes.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String(50), nullable=False)
    note_key = Column(Text, nullable=False)

    # Relationships
    note = relationship("Note", back_populates="collaborators")
    user = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Collaborator(note_id={self.note_id}, user_id={self.user_id}, \
                role={self.role}, note_key={self.note_key})>"
