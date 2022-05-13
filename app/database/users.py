from os import urandom
from hashlib import pbkdf2_hmac
from sqlalchemy import create_engine, String, Column
from sqlalchemy.ext.declarative import declarative_base
from . import Session


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    username = Column(String(50), primary_key=True)
    password_hash = Column(String(100), nullable=False)
    salt = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)


def hash_password(password: str, salt: bytes):
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return password_hash.hex()


async def validate_password(username: str, password: str):
    user = await get_user(username)
    password_hash = hash_password(password, bytes.fromhex(user.salt))
    return user.password_hash == password_hash


async def create_user(username: str, password: str, role="user"):
    random_bytes = urandom(16)
    print("RANDOM DONE")
    password_hash = hash_password(password, random_bytes)
    print("HASHED")
    user = User(username=username, password_hash=password_hash, salt=random_bytes.hex(), role=role)
    session = Session()
    session.add(user)
    session.commit()
    return True


async def get_user(username: str):
    session = Session()
    return session.query(User).get(username)


if __name__ == "__main__":
    engine = create_engine('sqlite://///sqlite3.db')
    engine.connect()
    Base.metadata.create_all(engine)
