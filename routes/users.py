from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from schemas.user import UserCreate, UserSignIn
from services.users import authenticate_user, save_user
from utils.shared import create_jwt, validation_error

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create")
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .join(User.logins)
        .filter(User.email == payload.email, 
                User.is_active == True,
            )
        .first()
    )
    
    if existing_user:
        filtered_user_logins = [
            login for login in existing_user.logins
            if login.method == 'email' and login.identifier == payload.identifier
        ]
        has_user_login = len(filtered_user_logins) > 0
        if has_user_login and payload.method == 'email':
            validation_error("email", "Email already exists.", "email")
    
    user = save_user(payload, db)

    if user:
        jwt_token = create_jwt({"user_id": user.id})
        response.set_cookie(key="jwt", value=jwt_token, httponly=True, max_age=60*60)

    return {"message": "User created successfully."}


@router.post('/login')
def login_user(payload: UserSignIn, response: Response, db: Session = Depends(get_db)):
    user_login = authenticate_user(payload, db)
    
    if not user_login['is_authenticated']:
        validation_error("credentials", "Invalid credentials.", "credentials", 401)

    jwt_token = create_jwt({"user_id": user_login['data'].user_id})

    response.set_cookie(key="jwt", value=jwt_token, httponly=True, max_age=60*60)

    return {"message": "Login successful."}