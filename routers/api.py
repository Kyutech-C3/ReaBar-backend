from typing import List
from sqlalchemy.orm.session import Session
from fastapi import APIRouter
from fastapi.params import Depends
from db.main import get_db
from cruds.api import create_report, get_books_by_id
from schemas.api import Book, Report
from fastapi_pagination import paginate
from fastapi_pagination import Page, paginate


router = APIRouter()

@router.get('/api/books/{user_id}', response_model=Page[Book])
async def books(user_id: str, db: Session = Depends(get_db)):
  books = get_books_by_id(db, user_id)
  return paginate(books)

@router.get('/api/reports/{user_id}', response_model=Report)
async def get_report(user_id: str, type: str = 'quantity', db: Session = Depends(get_db)):
  report = create_report(db, user_id, type)
  return report
