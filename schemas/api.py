from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

from db import models

class Book(BaseModel):
    isbn: str
    title: Optional[str]
    author: Optional[str]
    thumbnail_url: Optional[str]
    published_date: Optional[date]
    page: Optional[int]
    created_at: datetime = None
    
    class Config:
        orm_mode = True

class Read(BaseModel):
    user_id: str
    isbn: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class User(BaseModel):
    user_id: str
    name: str
    books: List[Book]
    read: List[Read]

    def from_orm_custom(orm: models.User):
        user = User.from_orm(orm)
        for i, read in enumerate(user.read):
            user.books[i].created_at = read.created_at
        del user.read
        return user

    class Config:
        orm_mode = True

class MockUser(BaseModel):
    user_id: str
    name: str
    books: List[Book]

class Report(BaseModel):
    months: List[str]
    data: List[int]
