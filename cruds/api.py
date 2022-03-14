from fastapi import HTTPException
from sqlalchemy.sql.functions import user
from db import models
from sqlalchemy.orm.session import Session
from schemas.api import User as UserSchema

def get_books_by_id(db: Session, user_id: str) -> UserSchema:
  user_orm = db.query(models.User).filter(models.User.user_id == user_id).first()
  if user_orm is None:
    raise HTTPException(
            status_code=404,
            detail="Not Found User"
        )
  user = UserSchema.from_orm_custom(user_orm)
  return user.books
