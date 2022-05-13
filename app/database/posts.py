from sqlalchemy import create_engine, String, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from . import Session
from uuid import uuid4


Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(String(50), primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(10000), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)


async def create_post(title: str, content: str):
    session = Session()
    post_id = str(uuid4())
    while session.query(Post).get(post_id):
        post_id = str(uuid4())
    post = Post(post_id=post_id, title=title, content=content, created_on=datetime.now())
    session.add(post)
    session.commit()
    return post_id


async def get_post(post_id: str):
    session = Session()
    return session.query(Post).get(post_id)


if __name__ == "__main__":
    engine = create_engine('sqlite://///sqlite3.db')
    engine.connect()
    Base.metadata.create_all(engine)
