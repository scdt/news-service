from fastapi import APIRouter, HTTPException
from app.database import posts


router = APIRouter()


@router.get("/")
async def root():
    return {"posts": {}}


@router.get("/{post_id}")
async def get_post(post_id):
    post = await posts.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=400, detail="Wrong post id")
    else:
        return {"title": post.title, "content": post.content}


@router.post("/")
async def create_post(title, text):
    try:
        post_id = await posts.create_post(title, text)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong")
        return
    return {"post_id": post_id}


@router.get("/{post_id}/delete")
async def delete_post(post_id):
    pass
