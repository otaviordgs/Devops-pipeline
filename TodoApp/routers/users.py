import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, APIRouter, status
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from .auth import get_current_user, get_user_exception, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404:{"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def get_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()

@router.get("/{user_id}")
async def get_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(new_password: str, user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()
    
    new_password_hash = get_password_hash(new_password)
    user = db.get(models.Users, user.get("id"))
    user.hashed_password = new_password_hash
    db.add(user)
    db.commit()

@router.delete("/")
async def delete_user(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    user = db.get(models.Users, user.get("id"))
    db.delete(user)
    db.commit()