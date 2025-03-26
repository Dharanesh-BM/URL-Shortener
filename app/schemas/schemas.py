from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class URLBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class URLCreate(URLBase):
    pass


class URL(URLBase):
    id: int
    short_code: str
    created_at: datetime
    is_active: bool
    owner_id: int
    visit_count: Optional[int] = 0
    short_url: Optional[str] = None

    class Config:
        from_attributes = True


class URLVisitBase(BaseModel):
    ip_address: str
    user_agent: str
    referrer: Optional[str] = None


class URLVisit(URLVisitBase):
    id: int
    url_id: int
    visited_at: datetime

    class Config:
        from_attributes = True 