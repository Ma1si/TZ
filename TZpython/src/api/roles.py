from sqlalchemy import select
from schemas.schemas import RoleCreate, PermissionCreate, RoleUpdate
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from utils.permissions import require_permission, require_admin
from utils.auth import get_current_user_id
from models.models import Users as User, Roles, Permissions

router = APIRouter(prefix="/admin", tags=["RBAC"])

@router.get("/roles/")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    await require_permission("admin:manage", db, current_user_id)
    stmt = select(Roles)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/roles/")
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("admin:manage", db, current_user_id)
    role = Roles(**role_in.dict())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("admin:manage", db, current_user_id)
    stmt = select(Roles).where(Roles.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role не найден")
    for field, value in role_in.dict(exclude_unset=True).items():
        setattr(role, field, value)
    await db.commit()
    await db.refresh(role)
    return role

@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("admin:manage", db, current_user_id)
    stmt = select(Roles).where(Roles.id == role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role не найден")
    await db.delete(role)
    await db.commit()
    return {"message": "Role удалён"}