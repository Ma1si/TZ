import hashlib
from select import select
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from models.models import Users
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password: str):
    password_bytes = hashlib.sha256(password.encode()).digest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = hashlib.sha256(password.encode()).digest()
    stored_hash = hashed_password.encode()
    return bcrypt.checkpw(password_bytes, stored_hash)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(token: str ) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id(token)
    stmt = select(Users).where(Users.id == user_id, Users.is_active == True)
    result = await  db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
        )
    return user
