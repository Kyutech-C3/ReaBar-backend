from calendar import month
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy.sql.functions import user
from db import models
from sqlalchemy.orm.session import Session
from schemas.api import Report, User as UserSchema

months_name = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
]

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
    months.append(labels[i])
  report = Report(
    months=months,
    data=data_list
  )
  return report
