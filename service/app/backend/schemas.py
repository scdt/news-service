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
    likes: int
    cringe: int
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
    id: int
    url: str
    owner: str
    likes: int
    cringe: int

    class Config:
        orm_mode = True


class Report(pydantic.BaseModel):
    id: int
    username: str
    post_id: int

    class Config:
        orm_mode = True


class AdvisoryMessage(pydantic.BaseModel):
    id: int
    username: str
    signature: str
