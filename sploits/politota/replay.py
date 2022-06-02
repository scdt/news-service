import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

DATABASE_URL = "sqlite:///../../service/app/backend/database.db"

engine = sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative.declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    username = sql.Column(sql.String(50), unique=True, nullable=False)
    realname = sql.Column(sql.String, nullable=False)
    password_hash = sql.Column(sql.String, nullable=False)

    posts = orm.relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = 'posts'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    owner_username = sql.Column(sql.String(
        50), sql.ForeignKey("users.username"))
    private = sql.Column(sql.Boolean, default=False)
    title = sql.Column(sql.String(100), nullable=False)
    content = sql.Column(sql.String(10000), nullable=False)

    user = orm.relationship("User", back_populates="posts")


users = Session().query(User).all()
for user in users:
    print(user.username)
