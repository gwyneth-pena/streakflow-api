from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin
from argon2 import PasswordHasher
from services.users import authenticate_user, save_user
from utils.shared import create_jwt, validation_error

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    
    if existing_user:
        validation_error("email", "Email already exists.", "email")
    
    hasher = PasswordHasher()
    hashed_password = hasher.hash(payload.password)
    payload.password = hashed_password
    
    save_user(payload, db)
    del payload.password

    return {"user": payload.model_dump()}


@router.post('/login')
def login_user(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user_login = authenticate_user(payload, db)
    
    if not user_login['is_authenticated']:
        validation_error("credentials", "Invalid credentials.", "credentials", 401)

    jwt_token = create_jwt({"user_id": user_login['data'].user_id})

    response.set_cookie(key="jwt", value=jwt_token, httponly=True, max_age=60*60)

    return {"message": "Login successful."}