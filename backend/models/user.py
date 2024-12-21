from sqlalchemy import Column, Integer, String
from db.connection import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, public_key={self.public_key})>"