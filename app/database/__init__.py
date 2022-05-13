from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///././sqlite3.db')
Session = sessionmaker(bind=engine)
