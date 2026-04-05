from schemas.schemas import PermissionCreate, PermissionUpdate
from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from utils.permissions import require_permission, require_admin
from utils.auth import get_current_user_id
from models.models import Permissions

router = APIRouter(prefix="/admin", tags=["RBAC"])

@router.post("/permissions")
async def create_permission(
    perm_in: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("manage", db, current_user_id)
    perm = Permissions(**perm_in.dict())
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm

@router.put("/permissions/{perm_id}")
async def update_permission(
    perm_id: int,
    perm_in: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("manage", db, current_user_id)
    stmt = select(Permissions).where(Permissions.id == perm_id)
    result = await db.execute(stmt)
    perm = result.scalar_one_or_none()
    if not perm:
        raise HTTPException(404, "Permission не найден")
    for field, value in perm_in.dict(exclude_unset=True).items():
        setattr(perm, field, value)
    await db.commit()
    await db.refresh(perm)
    return perm

@router.delete("/permissions/{perm_id}")
async def delete_permission(
    perm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await require_permission("manage", db, current_user_id)
    stmt = select(Permissions).where(Permissions.id == perm_id)
    result = await db.execute(stmt)
    perm = result.scalar_one_or_none()
    if not perm:
        raise HTTPException(404, "Permission не найден")
    await db.delete(perm)
    await db.commit()
    return {"message": "Permission удалён"}