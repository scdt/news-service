from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException
from db import get_user, create_user, validate_password

app = FastAPI()

'''
@app.on_event("startup")
async def start():
	pass

@app.on_event("shutdown")
async def stop():
	pass
'''

@app.get("/")
async def root():
	return {'Hello': 'World'}

@app.post("/sign-up")
async def register_user(username, password):
	if not password:
		raise HTTPException(status_code=400, detail="Empty password not allowed")
	user = await get_user(username)
	if user is not None:
		raise HTTPException(status_code=400, detail="User already exists")
	try:
		await create_user(username, password)
	except Exception as e:
		print(e)
		raise HTTPException(status_code=400, detail="Registration failed")
	return {"Status": "Ok"}
