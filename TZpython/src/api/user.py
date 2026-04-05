from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from schemas.schemas import UserUpdate, UserOut, UserDelete
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user_id, hash_password, verify_password
from models.models import Users
from db import get_db
from utils.permissions import require_permission

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/update")
async def data_update(user_data: UserUpdate, current_user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    stmt0 = select(Users.hash_password).where(current_user_id == Users.id)
    result = await db.execute(stmt0)
    data = result.first()
    hashed_password = data[0]

    values_update = {}

    if verify_password(user_data.password, hashed_password):
        if user_data.first_name is not None:
            values_update['first_name'] = user_data.first_name
        if user_data.last_name is not None:
            values_update['last_name'] = user_data.last_name
        if user_data.surname is not None:
            values_update['surname'] = user_data.surname
        if user_data.email is not None:
            values_update['email'] = user_data.email
        if user_data.new_password is not None:
            values_update['hash_password'] = hash_password(user_data.new_password)
    else:
        return HTTPException(status_code=400, detail='Пароль введен не верно')

    if values_update:
        stmt1 = update(Users).where(Users.id == current_user_id).values(**values_update)
        await db.execute(stmt1)
        await db.commit()
        return {"message": "Обновлено успешно", "updated_fields": list(values_update.keys())}

    return {
        "message": "что то пошло не так",
    }

@router.post("/delete")
async def data_delete(user_data: UserDelete, current_user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    id = current_user_id
    stmt0 = select(Users.hash_password).where(id == Users.id)
    result = await db.execute(stmt0)
    hashed_password = result.scalar()

    if verify_password(user_data.password, hashed_password):
        stmt = update(Users).where(id == Users.id).values(is_active=False)
        await db.execute(stmt)
        await db.commit()
        return {'message': 'пользователь удален'}
    else:
        return {'message': 'пароль введен не правильно'}

    return {'message' : 'что то пошло не так'}
