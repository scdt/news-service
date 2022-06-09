import fastapi
import fastapi.security as security
import jwt
import database as _db
import models
import schemas
import passlib.hash as hash
import sqlalchemy.orm as orm
from uuid import uuid4
import aiofiles
from exif import Image
from fastapi.responses import FileResponse
from ecdsa import VerifyingKey
from ecdsa.keys import BadSignatureError
import string


oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/token")
JWT_SECRET = "MYJWT@#$@#$@#dfsdfs"
advisory = 'advisory'
advisory_pk = VerifyingKey.from_string(
    b'\xd3|ei\x9b3\xf0\xf5\x84\xdf\x0c\xfc\x8a\xa0\xa1=\xc9\x18\xea\xf2\xee\x8a\x1e\x07\xdd\xb3\xb8,\xb2\x90\xa9(\xc7\tO\x8d\xbeAB\xd2\x1fW\xf0\xab\xa0-\xf0/')


async def add_to_db(db: orm.Session(), class_obj):
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)


def get_db():
    db = _db.Session()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_username(db: orm.Session(), username: str):
    return db.query(models.User).filter(models.User.username == username).first()


async def create_user(db: orm.Session(), user: schemas.UserCreate):
    user_obj = models.User(
        username=user.username,
        realname=user.realname,
        password_hash=hash.bcrypt.hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(db: orm.Session, username: str, password: str):

    user = await get_user_by_username(db, username)

    if (not user) or (not user.verify_password(password)):
        return False

    return user


async def create_token(user: models.User):
    user_obj = schemas.User.from_orm(user)

    payload = user_obj.dict()
    token = jwt.encode(payload, JWT_SECRET)

    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(
    db: orm.Session = fastapi.Depends(get_db),
    token: str = fastapi.Depends(oauth2schema),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid JWT token")

    return schemas.User.from_orm(user)


async def create_post(
    db: orm.Session,
    post: schemas.PostCreate,
    user: schemas.User
):
    post = models.Post(**post.dict(), owner_username=user.username)
    db.add(post)
    db.commit()
    db.refresh(post)

    return schemas.Post.from_orm(post)


async def get_posts(
    db: orm.Session,
    adv_msg: schemas.AdvisoryMessage = None
):
    if adv_msg is None:
        posts = db.query(models.Post).filter_by(
            private=False).order_by(models.Post.id.desc()).limit(20)
    elif verify_adv_msg(db, adv_msg):
        posts = db.query(models.Post).filter(
            models.Post.owner_username == adv_msg.username)
        report = db.query(models.Report).get(int(adv_msg.report_id))
        if report is not None:
            report.advised = True
            await add_to_db(db, report)
    else:
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")
    return list(map(schemas.Post.from_orm, posts))


async def get_top_posts(
    db: orm.Session
):
    posts = db.query(models.Post).filter_by(
        private=False).order_by((models.Post.likes+models.Post.cringe).desc()).limit(20)

    return list(map(schemas.Post.from_orm, posts))


async def get_top_images(
    db: orm.Session
):
    images = db.query(models.Image).order_by(
        (models.Image.likes+models.Image.cringe).desc()).limit(20)

    return list(map(schemas.Image.from_orm, images))


async def get_my_posts(
    db: orm.Session,
    user: schemas.User
):
    posts = db.query(models.Post).filter_by(
        owner_username=user.username).order_by(models.Post.id.desc())

    return list(map(schemas.Post.from_orm, posts))


async def get_post(
    db: orm.Session,
    post_id: int,
    user: schemas.User,
):
    post = db.query(models.Post).get(post_id)

    if post is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Post does not exist")

    if post.user.username == user.username or not post.private:
        return schemas.Post.from_orm(post)
    else:
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")


async def delete_post(
    db: orm.Session,
    post_id: int,
    user: schemas.User
):
    post = db.query(models.Post).get(post_id)

    if post is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Post does not exist")

    if post.user.username == user.username:
        db.delete(post)
        db.commit()
    else:
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")


async def report_post(
    db: orm.Session,
    post_id: int
):
    post = db.query(models.Post).get(post_id)

    if post is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Post does not exist")

    report = models.Report(username=post.user.username,
                           post_id=post.id, advised=False)
    db.add(report)
    db.commit()
    db.refresh(report)
    return schemas.Report.from_orm(report)


async def get_reports(
    db: orm.Session,
    user: schemas.User
):
    if user.username == advisory:
        reports = db.query(models.Report).filter(
            models.Report.advised == False).all()
        return list(map(schemas.Report.from_orm, reports))
    else:
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")


async def upload_image(
    db: orm.Session,
    input_file: fastapi.UploadFile,
    user: schemas.User
):

    for char in user.realname:
        if char not in string.printable:
            raise fastapi.HTTPException(
                400, detail="Russian letters in the real user name are not supported")

    for char in user.username:
        if char not in string.printable:
            raise fastapi.HTTPException(
                400, detail="Russian letters in the username are not supported")

    if input_file.content_type not in ["image/jpeg"]:
        raise fastapi.HTTPException(400, detail="Invalid document type")

    name = str(uuid4())
    while db.query(models.Image).filter_by(name=name).first() != None:
        name = str(uuid4())

    name += ".jpg"
    real_size = 0

    async with aiofiles.open(f"media/{name}", "wb") as out_file:
        while content := await input_file.read(1024):
            real_size += 1024

            if real_size > 1e6:
                raise fastapi.HTTPException(400, detail="File is too big")
            await out_file.write(content)

    with open(f"media/{name}", "rb") as image_file:
        my_image = Image(image_file)

    my_image.set("artist", user.realname)
    my_image.set("copyright", user.username)

    with open(f"media/{name}", "wb") as image_file:
        image_file.write(my_image.get_file())

    image = models.Image(owner=user.username, name=name,
                         url=f"/api/images/{name}")
    db.add(image)
    db.commit()
    db.refresh(image)

    return schemas.Image.from_orm(image)


async def get_image(
    db: orm.Session,
    name: str
):
    image = (
        db.query(models.Image)
        .filter_by(name=name)
        .first()
    )
    if image is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Image does not exist")

    name = schemas.Image.from_orm(image).url[11:]
    return FileResponse(f"media/{name}")


async def post_like(
    db: orm.Session,
    post_id: int,
    user: schemas.User
):
    post = db.query(models.Post).get(post_id)

    if (post is None) or (post.private == True):
        raise fastapi.HTTPException(
            status_code=404, detail="Post does not exist or private")

    user_like = db.query(models.PostLike).filter_by(
        post_id=post_id, user_id=user.id).first()

    if user_like is None:
        like = models.PostLike(user_id=user.id, post_id=post_id)
        post.likes += 1
        db.add(like)
        db.commit()
        db.refresh(like)
        return {"message": "liked"}
    else:
        post.likes -= 1
        db.delete(user_like)
        db.commit()
        return {"message": "unlike"}


async def post_cringe(
    db: orm.Session,
    post_id: int,
    user: schemas.User
):
    post = db.query(models.Post).get(post_id)

    if (post is None) or (post.private == True):
        raise fastapi.HTTPException(
            status_code=404, detail="Post does not exist or private")

    user_cringe = db.query(models.PostCringe).filter_by(
        post_id=post_id, user_id=user.id).first()

    if user_cringe is None:
        cringe = models.PostCringe(user_id=user.id, post_id=post_id)
        post.cringe += 1
        db.add(cringe)
        db.commit()
        db.refresh(cringe)
        return {"message": "cringed!"}
    else:
        post.cringe -= 1
        db.delete(user_cringe)
        db.commit()
        return {"message": "uncringe"}


async def image_like(
    db: orm.Session,
    image_id: int,
    user: schemas.User
):
    image = db.query(models.Image).get(image_id)

    if image is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Image does not exist")

    user_like = db.query(models.ImageLike).filter_by(
        image_id=image_id, user_id=user.id).first()

    if user_like is None:
        like = models.ImageLike(user_id=user.id, image_id=image_id)
        image.likes += 1
        db.add(like)
        db.commit()
        db.refresh(like)
        return {"message": "liked"}
    else:
        image.likes -= 1
        db.delete(user_like)
        db.commit()
        return {"message": "unlike"}


async def image_cringe(
    db: orm.Session,
    image_id: int,
    user: schemas.User
):
    image = db.query(models.Image).get(image_id)

    if image is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Image does not exist")

    user_cringe = db.query(models.ImageCringe).filter_by(
        image_id=image_id, user_id=user.id).first()

    if user_cringe is None:
        cringe = models.ImageCringe(user_id=user.id, image_id=image_id)
        image.cringe += 1
        db.add(cringe)
        db.commit()
        db.refresh(cringe)
        return {"message": "cringed!"}
    else:
        image.cringe -= 1
        db.delete(user_cringe)
        db.commit()
        return {"message": "uncringe"}


async def get_images(db: orm.Session):
    images = db.query(models.Image).order_by(models.Image.id.desc()).limit(20)
    return list(map(schemas.Image.from_orm, images))


def verify_adv_msg(db: orm.Session(), adv_msg: schemas.AdvisoryMessage):
    signature = bytearray.fromhex(adv_msg.signature)
    try:
        advisory_pk.verify(signature, str.encode(adv_msg.username))
        return True
    except BadSignatureError:
        return False
