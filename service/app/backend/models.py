import sqlalchemy as sql
import sqlalchemy.orm as orm
import passlib.hash as hash
import database as db


class User(db.Base):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    username = sql.Column(sql.String(50), unique=True, nullable=False)
    realname = sql.Column(sql.String, nullable=False)
    password_hash = sql.Column(sql.String, nullable=False)

    posts = orm.relationship("Post", back_populates="user")

    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.password_hash)


class Post(db.Base):
    __tablename__ = 'posts'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    owner_username = sql.Column(sql.String(
        50), sql.ForeignKey("users.username"))
    private = sql.Column(sql.Boolean, default=False)
    title = sql.Column(sql.String(100), nullable=False)
    content = sql.Column(sql.String(10000), nullable=False)

    user = orm.relationship("User", back_populates="posts")


class Image(db.Base):
    __tablename__ = 'images'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    owner_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    name = sql.Column(sql.String(100), unique=True)
    url = sql.Column(sql.String(100), unique=True)


class Report(db.Base):
    __tablename__ = 'reports'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    username = sql.Column(sql.String(50), unique=False, nullable=False)
    post_id = sql.Column(sql.Integer, unique=False, nullable=False)
    advised = sql.Column(sql.Integer, unique=False, nullable=False)


if __name__ == "__main__":
    db.Base.metadata.create_all(bind=db.engine)
    session = db.Session()
    user = User(username='advisory', realname='advisory', password_hash='$2b$12$f1v528t5SgabhnlQnQcIuunH.n.IuKogF6IKYHSPV.IFOb.9nOKXG')
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
