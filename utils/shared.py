

from fastapi import HTTPException
from argon2 import PasswordHasher
import jwt
from datetime import datetime, timedelta

from config import SECRET_KEY

def validation_error(field: str, msg: str, type_: str, status: int = 422):
    raise HTTPException(
        status_code=status,
        detail=[{
            "loc": ["body", field],
            "msg": msg,
            "type": type_,
        }]
    )

def verify_password(plain_password: str, hashed_password: str):
    try:
        hasher = PasswordHasher()
        return hasher.verify(hashed_password, plain_password)
    except Exception:
        return False
    
def create_jwt(data: dict, expires_in_minutes: int = 60):
    payload = data.copy()
    expires = datetime.now() + timedelta(minutes=expires_in_minutes)
    payload['exp'] = expires
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        validation_error("token", "Token has expired.", "token.expired", status=401)
    except jwt.InvalidTokenError:
        validation_error("token", "Invalid token.", "token.invalid", status=401)