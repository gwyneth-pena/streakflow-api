
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from db import Base

class UserLogin(Base):
    __tablename__ = "user_logins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    method = Column(String(50), nullable=False)
    identifier = Column(String(300), nullable=False)
    password = Column(String(200), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='logins')