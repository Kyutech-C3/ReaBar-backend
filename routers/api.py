from typing import List
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi import APIRouter
from fastapi.params import Depends
from db.main import get_db
from cruds.api import get_books_by_id
from schemas.api import Book

router = APIRouter()

@router.get('/books/{user_id}', response_model=List[Book])
async def books(user_id: str, db: Session = Depends(get_db)):
  books = get_books_by_id(db, user_id)
  return books
