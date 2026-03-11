from pydantic import BaseModel
from typing import Optional #For optional fields, in this case description
from datetime import datetime

# When user registers
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# When user logs in
class UserLogin(BaseModel):
    username: str
    password: str

# What we send back after user registers
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True  # Convert database objects to JSON to allow for easy response

# When creating a task
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None  # Optional field, defaults to None if not provided

# When updating a task
class TaskUpdate(BaseModel):
    title: Optional[str] = None  # All fields optional sice we might only want to update one of them
    description: Optional[str] = None
    completed: Optional[bool] = None

# What we send back after task operations
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# What we send back after login
class Token(BaseModel):
    access_token: str  # The JWT token
    token_type: str  # Always "bearer", tells the client how to use the token