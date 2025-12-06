
from models.user import User
from models.user_login import UserLogin
from schemas.user import UserCreate
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.shared import verify_password


def save_user(payload: UserCreate, db: Session):
    user = User(firstname=payload.firstname, lastname=payload.lastname, email=payload.email)
    user_login = UserLogin(
        user=user,
        method=payload.method,
        identifier=payload.identifier,
        password=payload.password
    )
    user.logins.append(user_login)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(payload: UserLogin, db: Session):
        
    user_login = db.query(UserLogin).filter(
        UserLogin.method == payload.method,
        UserLogin.identifier == payload.identifier
    ).first()

    if user_login is None:
        return {
            'is_authenticated': False,
            'data': None
        }

    if payload.password:
        is_correct_password = verify_password(payload.password, user_login.password)
    
    if  not is_correct_password:
        return {
            'is_authenticated': False,
            'data': None
        }
    
    user_login.last_login_at = func.now()
    db.commit()
    
    return {
        'is_authenticated': True,
        'data': user_login
    }