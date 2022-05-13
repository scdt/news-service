from fastapi import APIRouter, HTTPException
from app.database import users


router = APIRouter()


@router.post("/sign-up")
async def create_user(username, password):
    print("Create User Start")
    if not password:
        raise HTTPException(status_code=400, detail="Empty password not allowed")
        return
    user = await users.get_user(username)
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")
        return
    try:
        await users.create_user(username, password)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Registration failed")
        return
    return {"Status": "Ok"}


@router.post("/auth")
async def auth(username, password):
    user = await users.get_user(username)
    if user is None:
        raise HTTPException(status_code=400, detail="Wrong password")
        return
    if await users.validate_password(username, password):
        return {"Status": "Ok"}
    else:
        raise HTTPException(status_code=400, detail="Wrong password")


@router.get("/users/update-role")
async def update_role(username):
    pass
