import fastapi
import fastapi.security as security
import jwt
import database as _db
import models, schemas
import passlib.hash as hash
import sqlalchemy.orm as orm
from uuid import uuid4
import aiofiles
from exif import Image
from fastapi.responses import FileResponse

oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/token")
JWT_SECRET = "MYJWT@#$@#$@#dfsdfs"

def create_database():
    return _db.Base.metadata.create_all(bind=_db.engine)

def get_db():
    db = _db.Session()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_username(username: str, db: orm.Session()):
    return db.query(models.User).filter(models.User.username == username).first()

async def create_user(user: schemas.UserCreate, db: orm.Session()):
    user_obj = models.User(
        username = user.username, 
        realname = user.realname,
        password_hash = hash.bcrypt.hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(username:str, password:str, db: orm.Session):

    user = await get_user_by_username(username, db)

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
            status_code=401, 
            detail="Invalid JWT token"
            )
    
    return schemas.User.from_orm(user)

async def create_post(
    post: schemas.PostCreate,
    user: schemas.User,
    db: orm.Session
):
    post = models.Post(**post.dict(), owner_username=user.username)
    db.add(post)
    db.commit()
    db.refresh(post)

    return schemas.Post.from_orm(post)

async def get_posts(
    db: orm.Session
    ):
    posts = db.query(models.Post).filter_by(private=False).order_by(models.Post.id.desc()).limit(20)

    return list(map(schemas.Post.from_orm, posts))

async def get_my_posts(
    user: schemas.User,
    db: orm.Session
    ):
    posts = db.query(models.Post).filter_by(owner_username=user.username).order_by(models.Post.id.desc())

    return list(map(schemas.Post.from_orm, posts))
    
async def _post_selector(post_id: int, user: schemas.User, db: orm.Session):
    post = (
        db.query(models.Post)
        .filter_by(owner_username=user.username)
        .filter(models.Post.id == post_id)
        .first()
    )
    
    if post is None:
        raise fastapi.HTTPException(status_code=404, detail="Post does not exist")
    
    return post

async def get_post(post_id: int, user: schemas.User, db: orm.Session):
    post = await _post_selector(post_id=post_id, user=user, db=db)
    return schemas.Post.from_orm(post)

async def delete_post(post_id: int, user: schemas.User, db: orm.Session):
    post = await _post_selector(post_id, user, db)

    db.delete(post)
    db.commit()

async def upload_image(
    input_file: fastapi.UploadFile,
    user: schemas.User,
    db: orm.Session
):

    print(user.realname)
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

    my_image.set("artist",user.realname)
    my_image.set("copyright", user.username)

    with open(f"media/{name}", "wb") as image_file:
        image_file.write(my_image.get_file())

    image = models.Image(owner_id=user.id, name=name, url=f"api/images/{name}")
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return schemas.Image.from_orm(image)

async def get_image(name: str, db: orm.Session):
    image = (
        db.query(models.Image)
        .filter_by(name=name)
        .first()
    )
    if image is None:
        raise fastapi.HTTPException(status_code=404, detail="Image does not exist")
    
    name = schemas.Image.from_orm(image).url[11:]
    return FileResponse(f"media/{name}")

async def get_images(db: orm.Session):
    images = db.query(models.Image).order_by(models.Image.id.desc()).limit(20)
    return list(map(schemas.Image.from_orm, images))