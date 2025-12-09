
from models.user import User
from models.user_login import UserLogin
from schemas.user import UserCreate
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.shared import decode_and_verify_google_token, verify_password


def save_user(payload: UserCreate, db: Session):
    if payload.method != 'email':
        decoded_google_token = decode_and_verify_google_token(payload.token)

        payload.email = decoded_google_token.get('email')
        payload.identifier = decoded_google_token.get('sub')
        payload.firstname = decoded_google_token.get('given_name')
        payload.lastname = decoded_google_token.get('family_name')

    
    user = (
        db.query(User)
        .join(User.logins)
        .filter(
                User.is_active == True,
                User.email == payload.email,
            )
        .first()
    )
        
    if user is None:
        user = User(firstname=payload.firstname, lastname=payload.lastname, email=payload.email)
    
    has_user_login = False
    if user:
        filtered_user_logins = [
            login for login in user.logins
            if login.method == payload.method and login.identifier == payload.identifier
        ]
        has_user_login = len(filtered_user_logins) > 0

    if has_user_login:
        return user

    user_login = UserLogin(
        user=user,
        method=payload.method,
        identifier=payload.identifier,
        password=payload.password,
        last_login_at=func.now()
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