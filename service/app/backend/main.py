import fastapi
import fastapi.security as security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlalchemy.orm as orm
import services
import schemas
from typing import List

app = fastapi.FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/users")
async def create_user(
    user: schemas.UserCreate,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    db_user = await services.get_user_by_username(user.username, db)
    if db_user:
        raise fastapi.HTTPException(
            status_code=400, detail="User already exist")

    user = await services.create_user(user, db)

    return await services.create_token(user)


@app.post("/api/token")
async def generate_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    user = await services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")
    return await services.create_token(user)


@app.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user


@app.post("/api/posts", response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.create_post(post=post, user=user, db=db)


@app.get("/api/posts", response_model=List[schemas.Post])
async def get_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts(db=db)


@app.get("/api/posts/my", response_model=List[schemas.Post])
async def get_my_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_my_posts(user=user, db=db)


@app.get("/api/posts/{post_id}", status_code=200)
async def get_post(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_post(post_id, user, db)


@app.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    await services.delete_post(post_id, user, db)

    return {"message": "Sucessfully deleted"}


@app.post("/api/images/", response_model=schemas.Image)
async def upload_image(
    file: fastapi.UploadFile,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    print(1)
    return await services.upload_image(
        input_file=file,
        user=user,
        db=db
    )


@app.get("/api/images/")
async def get_images(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_images(db=db)


@app.get("/api/images/{image_name}")
async def get_image(
    image_name: str,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_image(name=image_name, db=db)


@app.get("/api")
async def root():
    return {"Messages": "Politota"}
