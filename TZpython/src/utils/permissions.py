from select import select
from jose import jwt
from utils.auth import get_current_user
from models.models import Users, Roles, Permissions
from db import get_db
from sqlalchemy import select, exists
from models.models import role_permissions, user_roles
from utils.auth import get_current_user_id
from utils.auth import oauth2_scheme
from config import ALGORITHM, SECRET_KEY
from schemas.schemas import RoleUpdate
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def require_admin(token: str, db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(400, "Требуется token в query (?token=...)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        roles = payload.get("roles", [])

        if "admin" not in roles:
            raise HTTPException(401, f"Токен не админа. Роли: {roles}")
        return {"id": user_id, "roles": roles, "is_admin": True}
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Токен истёк")
    except jwt.JWTError as e:
        print(f"JWT ERROR: {e}")
        raise HTTPException(401, f"Неверный токен: {str(e)}")


async def require_permission(permission_name: str, db: AsyncSession, current_user_id: int):
    stmt = select(
        exists().where(
            user_roles.c.user_id == current_user_id,
            user_roles.c.role_id == role_permissions.c.role_id,
            role_permissions.c.permission_id == Permissions.id,
            Permissions.name == permission_name,
        )
    )
    result = await db.execute(stmt)
    if not result.scalar():
        raise HTTPException(403, "Forbidden")