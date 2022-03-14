from typing import Any
from sqlalchemy import Boolean, Column, Date, DateTime, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.orm import relationship
from uuid import uuid4

@as_declarative()
class Base:
	id: Any
	__name__: Any

def generate_uuid():
	return str(uuid4())

class Read(Base):
	__tablename__ = 'reads'
	user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
	isbn = Column(String, ForeignKey('books.isbn'), primary_key=True)
	created_at = Column(DateTime, default=func.now())

class User(Base):
	__tablename__ = 'users'
	user_id = Column(String, primary_key=True)
	name = Column(String)

	books = relationship('Book', secondary=Read.__tablename__, backref='Book')
	read = relationship('Read')

class Book(Base):
	__tablename__ = 'books'
	isbn = Column(String, primary_key=True)
	title = Column(String, nullable=True)
	author = Column(String, nullable=True)
	thumbnail_url = Column(String, nullable=True)
	published_date = Column(Date, nullable=True)
	page = Column(Integer, nullable=True)

	users = relationship('User', secondary=Read.__tablename__)

class ReadPage(Base):
	__tablename__ = 'read_pages'
	user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
	year = Column(Integer, primary_key=True)
	month = Column(Integer, primary_key=True)
	week = Column(Integer, primary_key=True)
	pages = Column(Integer)
	quantity = Column(Integer)
