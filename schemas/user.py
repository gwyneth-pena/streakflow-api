
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator



class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: Optional[str] = Field(None, min_length=8)
    method: str = 'email'
    identifier: Optional[str] = None

    @model_validator(mode='after')
    def check_method(cls, values):

        method = values.method
        password = values.password

        if method == 'email' and password is None:
            raise ValueError('Email method requires a password')
        elif method == 'email' and password is not None: 
            values.identifier = values.email
        return values
    

class UserLogin(BaseModel):
    method: str
    identifier: str
    password: Optional[str] = None