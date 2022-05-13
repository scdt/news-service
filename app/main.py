from fastapi import FastAPI
import app.database
from app.routers import users, posts


app = FastAPI()


@app.on_event("startup")
async def start():
    pass


@app.on_event("shutdown")
async def stop():
    pass


app.include_router(users.router)
app.include_router(posts.router)
