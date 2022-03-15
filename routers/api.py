from enum import Enum, auto
from typing import List
from sqlalchemy.orm.session import Session
from fastapi import APIRouter
from fastapi.params import Depends
from db.main import get_db
from cruds.api import create_report, get_ranking, get_books_order_by_query, get_total_info
from schemas.api import Book, RankingUser, Report, TotalInfo
from fastapi_pagination import paginate
from fastapi_pagination import Page, paginate

class ModelName(str, Enum):
    title = "title"
    author = "author"
    published_date = "published_date"
    created_at = "created_at"

class Type(str, Enum):
    quantity = "quantity"
    page = "page"

router = APIRouter()

@router.get('/api/books/total/{user_id}', response_model=TotalInfo)
async def get_total(user_id: str, db: Session = Depends(get_db)):
  total_info = get_total_info(db, user_id)
  return total_info

@router.get('/api/books/{user_id}', response_model=Page[Book])
async def books(user_id: str, order_by: ModelName, db: Session = Depends(get_db)):
  books = get_books_order_by_query(db, user_id, order_by.value)

  return paginate(books)

@router.get('/api/reports/{user_id}', response_model=Report)
async def get_report(user_id: str, type: Type, db: Session = Depends(get_db)):
  report = create_report(db, user_id, type)
  return report

@router.get('/api/ranking', response_model=List[RankingUser])
async def get_read_info_ranking(type: Type, db: Session = Depends(get_db)):
  ranking = get_ranking(db, type)
  return ranking
