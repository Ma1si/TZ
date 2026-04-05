from fastapi import HTTPException
from sqlalchemy import select
from fastapi import APIRouter, Depends
from schemas.schemas import UserCreate, UserLog
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Users
from db import get_db
from utils.auth import hash_password, create_access_token, verify_password
from config import ALGORITHM, SECRET_KEY
from models.models import Roles
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    if user_data.password != user_data.password_confirm:
        raise HTTPException(status_code=400, detail='Пароли не совпадают')

    stmt = select(Users).where(Users.email == user_data.email)
    res = await db.execute(stmt)
    existing = res.scalars().first()

    if existing:
        raise HTTPException(status_code=400, detail='Пользователь с этой почтой уже зарегестрирован')

    user = Users(
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        surname = user_data.surname,
        email = user_data.email,
        hash_password = hash_password(user_data.password)
    )

    role_stmt = select(Roles).where(Roles.name == "user")
    role_res = await db.execute(role_stmt)
    user_role = role_res.scalars().first()
    user.roles.append(user_role)



    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {'message': 'успешно', 'data': user}

@router.post("/login")
async def login(user: UserLog, db: AsyncSession = Depends(get_db)):
    stmt = select(Users).options(selectinload(Users.roles)).where(
        Users.email == user.email,
        Users.is_active != False
    )
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=400, detail='Пользователь не найден')

    if not verify_password(user.password, db_user.hash_password):
        raise HTTPException(status_code=400, detail='Неверный пароль')

    roles = [role.name for role in db_user.roles]

    return {
        'access_token': create_access_token({
            'sub': str(db_user.id),
            'user_id': db_user.id,
            'roles': roles
        }),
        'id': db_user.id,
        'roles': roles
    }
    return HTTPException(status_code=400, detail='Неверный пароль')

