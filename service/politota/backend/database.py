import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

DATABASE_URL = "sqlite:///./db/database.db"

engine = sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative.declarative_base()
