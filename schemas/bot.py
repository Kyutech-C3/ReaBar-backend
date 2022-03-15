from pydantic import BaseModel

from db import models

class User(BaseModel):
    user_id: str
    name: str

    class Config:
        orm_mode = True