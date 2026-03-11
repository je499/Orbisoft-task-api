from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from models import Base, User, Task
from schemas import (
    UserCreate, UserLogin, UserResponse, TaskCreate, TaskUpdate, 
    TaskResponse, Token
)

#Database setup
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in database
Base.metadata.create_all(bind=engine)

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

#Dependencies

# Get database session for endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Verify user token and return user object
def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Helper Functions

# Hash a password using bcrypt
def hash_password(password):
    return pwd_context.hash(password)

# Check if plain password matches hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT token for user
def create_access_token(username, expires_delta=None):
    if expires_delta is None:
        expires_delta = timedelta(hours=24)  # Token expires in 24 hours
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# APP Setup
app = FastAPI(
    title="Task API",
    description="Simple task management API",
    version="1.0.0"
)

# Endpoints

# Create new user account
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# Login user and get token
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(User).filter(User.username == user.username).first()
    
    # Check username and password
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create and return token
    access_token = create_access_token(username=db_user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# Create a new task
@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    # Get current user from token
    current_user = get_current_user(token=token, db=db)
    
    # Create task linked to this user
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


# Get all tasks for current user
@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(token: str = None, db: Session = Depends(get_db)):
    # Get current user from token
    current_user = get_current_user(token=token, db=db)
    
    # Get all tasks for this user
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


# Update a task
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    token: str = None,
    db: Session = Depends(get_db)
):
    # Get current user from token
    current_user = get_current_user(token=token, db=db)
    
    # Find task that belongs to this user
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update only fields that were provided
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.completed is not None:
        db_task.completed = task_update.completed
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    # Get current user from token
    current_user = get_current_user(token=token, db=db)
    
    # Find task that belongs to this user
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Delete task
    db.delete(db_task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


# Test endpoint
@app.get("/")
def read_root():
    return {"message": "Task API is running! Visit /docs for API documentation"}