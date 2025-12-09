
from typing import Optional
from argon2 import PasswordHasher
from pydantic import model_validator

from schemas.shared import TrimmedBaseModel

class UserCreate(TrimmedBaseModel):
    firstname: str
    lastname: str
    email: Optional[str] = None 
    password: Optional[str] = None
    method: str = 'email'
    identifier: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode='before')
    def normalize_fields(cls, values):
        if values.get("identifier"):
            values["identifier"] = values["identifier"].lower()

        if values.get("email"):
            values["email"] = values["email"].lower()

        if values.get("method"):
            values["method"] = values["method"].lower()

        if values.get("firstname"):
            values["firstname"] = values["firstname"].title()

        if values.get("lastname"):
            values["lastname"] = values["lastname"].title()
        return values

    @model_validator(mode='after')
    def validate_fields(cls, values):

        method = values.method
        email = values.email
        password = values.password
        token = values.token

        if method == 'email':
            if not email:
                raise ValueError('Email is required for email signup.')
            if '@' not in email:
                raise ValueError('Email must be valid.')
            if not password or len(password) < 8:
                raise ValueError('Password is required and must be at least 8 characters for email signup.')
            values.identifier = email
        else:
            if not token:
                raise ValueError(f'{method} auth method requires a token.')
            
        if values.password:
            hasher = PasswordHasher()
            hashed_password = hasher.hash(values.password)
            values.password = hashed_password
            
        return values
    

class UserSignIn(TrimmedBaseModel):
    method: str
    identifier: str
    password: Optional[str] = None