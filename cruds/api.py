from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy import func
from db import models
from sqlalchemy.orm.session import Session
from schemas.api import Ranking, RankingUser, Report, User as UserSchema

def get_books_by_id(db: Session, user_id: str) -> UserSchema:
  user_orm = db.query(models.User).filter(models.User.user_id == user_id).first()
  if user_orm is None:
    raise HTTPException(
            status_code=404,
            detail="Not Found User"
        )
  user = UserSchema.from_orm_custom(user_orm)
  return user.books

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

def get_ranking(db: Session, type: str) -> Ranking:
  if not type in ['quantity', 'page']:
    raise HTTPException(status_code=400, detail='invalid query')
  now = datetime.now()
  q = db.query(models.ReadPage.user_id, models.User.name, func.sum(models.ReadPage.quantity).label('qnt'), func.sum(models.ReadPage.pages).label('pg')).filter(models.ReadPage.year == now.year, models.ReadPage.month == now.month).group_by(models.ReadPage.user_id, models.User.name)
  
  if type == 'quantity':
    q = q.order_by('qnt')
  if type == 'page':
    q = q.order_by('pg')
  q.limit(5)

  ranking = []

  for uid, name, qnt, pg in q:
    ru = RankingUser(
      user_id=uid,
      name=name,
      quantity=qnt,
      page=pg
    )
    ranking.append(ru)
  return Ranking(
    type=type,
    ranking=ranking
  )
