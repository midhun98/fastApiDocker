from typing import Annotated
from fastapi import Depends, FastAPI, BackgroundTasks
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

# intialize DB
Base.metadata.create_all(bind=engine)

@app.get("/user/")
async def get_users(db:db_dependency):
    users = db.query(User).all()
    return users

@app.post("/user/")
async def create_user(name: str, background_tasks: BackgroundTasks, db:db_dependency):
    user = User(name=name)
    db.add(user)
    db.commit()
    background_tasks.add_task(print_message, name)
    return {"name": name, "message": "User created successfully"}

async def print_message(name: str):
    print(f"User {name} created successfully")