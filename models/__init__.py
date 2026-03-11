from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Create base class for all models
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # Must be unique
    email = Column(String, unique=True, index=True)  # Must be unique
    hashed_password = Column(String)  # Never store plain passwords
    
    # Link to all tasks belonging to this user
    tasks = relationship("Task", back_populates="owner")


# Task table
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)  # Default is not completed
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto timestamps to track when task was created
    
    user_id = Column(Integer, ForeignKey("users.id"))  # Links to user
    owner = relationship("User", back_populates="tasks")  # Link back to user