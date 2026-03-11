from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# This creates the base class that all our database models inherit from
# Every model needs to inherit from Base
Base = declarative_base()

# This represents a user in the database, can have several tasks per user
class User(Base):
    __tablename__ = "users"  # The name of the table
    
    # Database columns (fields that will be stored)
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each user 
    username = Column(String, unique=True, index=True)  # Username must be unique, indexed 
    email = Column(String, unique=True, index=True)  # Email must be unique, indexed 
    hashed_password = Column(String)  # Password stored as a hash, keeps it secure
    
    # This creates a relationship so we can easily access all tasks for a user
    tasks = relationship("Task", back_populates="owner")



#Task Model
# This represents a task (to-do item) in the database
# Each task belongs to exactly one user
class Task(Base):
    __tablename__ = "tasks"  # The name of the table
    
    # Database columns (fields that will be stored)
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each task 
    title = Column(String, index=True)  # Task title, indexed for fast searches
    description = Column(String)  # Optional longer description of the task
    completed = Column(Boolean, default=False)  # Whether the task is done - the default is False
    created_at = Column(DateTime, default=datetime.utcnow)  # When the task was created (automatic timestamp)
    
    # Foreign key - links this task to a user, ensures that every task belongs to a user
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # This creates a relationship so we can easily access the owner of a task
    owner = relationship("User", back_populates="tasks")