from email.policy import default
import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
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
    likes = sql.Column(sql.Integer, default=0)
    cringe = sql.Column(sql.Integer, default=0)


class Image(db.Base):
    __tablename__ = 'images'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    owner = sql.Column(sql.String(50), sql.ForeignKey("users.username"))
    name = sql.Column(sql.String(100), unique=True)
    url = sql.Column(sql.String(100), unique=True)

    likes = sql.Column(sql.Integer, default=0)
    cringe = sql.Column(sql.Integer, default=0)


class Report(db.Base):
    __tablename__ = 'reports'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    username = sql.Column(sql.String(50), unique=False, nullable=False)
    post_id = sql.Column(sql.Integer, unique=False, nullable=False)

class PostLike(db.Base):
    __tablename__ = 'post_like'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    post_id = sql.Column(sql.Integer, sql.ForeignKey("posts.id"))

class PostCringe(db.Base):
    __tablename__ = 'post_cringe'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    post_id = sql.Column(sql.Integer, sql.ForeignKey("posts.id"))

class ImageLike(db.Base):
    __tablename__ = 'image_like'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    image_id = sql.Column(sql.Integer, sql.ForeignKey("images.id"))

class ImageCringe(db.Base):
    __tablename__ = 'image_cringe'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    image_id = sql.Column(sql.Integer, sql.ForeignKey("images.id"))

if __name__ == "__main__":
    db.Base.metadata.create_all(bind=db.engine)
