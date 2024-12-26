from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from db.connection import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password_hash = Column(Text, nullable=False)
    #password_salt = Column(String(255), nullable=False)
    public_key = Column(Text, nullable=False)

    # Relationship with notes as collaborators
    notes = relationship("Collaborator", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, public_key={self.public_key})>"