from typing import List
import datetime as dt
import pydantic

class _PostBase(pydantic.BaseModel):
    title: str
    content: str

class PostCreate(_PostBase):
    private: bool

class Post(_PostBase):
    id: int
    owner_username: str

    class Config:
        orm_mode = True
    
class _UserBase(pydantic.BaseModel):
    username: str
    realname: str

class UserCreate(_UserBase):
    password: str

class User(_UserBase):
    id: int

    class Config:
        orm_mode = True

class Image(pydantic.BaseModel):
    url: str

    class Config:
        orm_mode = True


    