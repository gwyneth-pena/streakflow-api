from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from schemas.user import UserCreate
from argon2 import PasswordHasher
from services.users import save_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")
    
    hasher = PasswordHasher()
    hashed_password = hasher.hash(payload.password)
    payload.password = hashed_password
    
    save_user(payload, db)
    del payload.password

    return {"user": payload.model_dump()}