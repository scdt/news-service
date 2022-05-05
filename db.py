import json
from uuid import uuid4
import hashlib
import os


def hash_password(password: str, salt: bytes):
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hashed.hex()

async def get_user(username: str):
	with open("db.json", "r") as file:
		db = json.load(file)
		return db["users"].get(username)

async def validate_password(username: str, password: str):
	with open("db.json", "r") as file:
		db = json.load(file)
		hashed_password = hash_password(password, bytes.fromhex(db["users"][username]["salt"]))
		return hashed_password.hex() == db["users"][username]["password"]

async def create_user(username: str, password: str, role="user"):
	with open("db.json", "r+") as file:
		db = json.load(file)
		random_bytes = os.urandom(16)
		hashed_password = hash_password(password, random_bytes)
		db["users"][username] = {"password": hashed_password, "salt": random_bytes.hex(), "role": role}
		file.seek(0)
		json.dump(db, file, indent=4)
		file.truncate()