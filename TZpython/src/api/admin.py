from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from models.models import Permissions
from utils.permissions import require_permission
from utils.auth import get_current_user_id
from schemas.schemas import RoleUpdate
from utils.permissions import require_admin
from models.models import Users as User, Roles
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/admin", tags=["RBAC"])

@router.get("/")
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("admin:manage", db, current_user_id)
    stmt = select(Permissions)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/users/{user_id}/roles")
async def update_roles(
    user_id: int,
    data: RoleUpdate,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).options(selectinload(User.roles)).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


    stmt = select(Roles.name).where(Roles.name == data.roles[0])
    result = await db.execute(stmt)
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=400, detail="Недопустимые роли")


    user.roles.clear()
    for r_name in data.roles:
        role_stmt = select(Roles).where(Roles.name == r_name)
        role_result = await db.execute(role_stmt)
        role_obj = role_result.scalar_one_or_none()
        if role_obj:
            user.roles.append(role_obj)

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Роли заменены",
        "user_id": user.id,
        "roles": [r.name for r in user.roles],
        "admin_id": admin["id"]
    }

