from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy import desc, func
from db import models
from sqlalchemy.orm.session import Session
from schemas.api import RankingUser, Book, Report, User as UserSchema

def get_books_order_by_query(db: Session, user_id: str, order_by: str) -> List[Book]:
  
  user_orm = db.query(models.User).filter(models.User.user_id == user_id).first()
  
  if user_orm is None:
    raise HTTPException(
            status_code=404,
            detail="Not Found User"
        )
  user = UserSchema.from_orm_custom(user_orm)
  books = user.books
  if(order_by == "title"):
    books = sorted(books, key=lambda x:x.title)

  if(order_by == "author"):
    books = sorted(books, key=lambda x: x.author)
  
  if(order_by == "published_date"):
    books = sorted(books, key=lambda x: x.published_date)
  
  if(order_by == "created_at"):
    books = sorted(books, key=lambda x: x.created_at)

  return books


def create_report(db: Session, user_id: str, type: str) -> Report:
  if not type in ['quantity', 'page']:
    raise HTTPException(status_code=400, detail='invalid query')
  now = datetime.now()
  months_name = list(range(12))
  labels = months_name[now.month:]+months_name[:now.month]
  print(labels)
  months = []
  data_list = []
  for i in range(12):
    previous = now - relativedelta(months=11-i)
    read_pages = db.query(models.ReadPage).filter(models.ReadPage.user_id == user_id, models.ReadPage.year == previous.year, models.ReadPage.month == previous.month).all()
    if len(read_pages) == 0 and len(months) == 0:
      continue
    data = 0
    if type == 'page':
      for read_page in read_pages:
        data += read_page.pages
    elif type == 'quantity':
      for read_page in read_pages:
        data += read_page.quantity
    data_list.append(data)
    months.append(labels[i]+1)
  report = Report(
    months=months,
    data=data_list
  )
  return report

def get_ranking(db: Session, type: str) -> List[RankingUser]:
  if not type in ['quantity', 'page']:
    raise HTTPException(status_code=400, detail='invalid query')
  now = datetime.now()

  if type == 'quantity':
    q = db.query(models.User.user_id, models.User.name, func.sum(models.ReadPage.quantity).label('val'))
  if type == 'page':
    q = db.query(models.User.user_id, models.User.name, func.sum(models.ReadPage.pages).label('val'))
  
  q = q.filter(models.ReadPage.year == now.year, models.ReadPage.month == now.month, models.User.user_id == models.ReadPage.user_id).group_by(models.User.user_id, models.User.name).order_by(desc('val'))

  print(q)

  ranking = []
  for uid, name, val in q:
    ranking.append(RankingUser(
      user_id=uid,
      name=name,
      value=val
    ))
  
  return ranking
