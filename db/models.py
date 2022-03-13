import datetime
from typing import Any
from sqlalchemy import Boolean, Column, DateTime, func
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
