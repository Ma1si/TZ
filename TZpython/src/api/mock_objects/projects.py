from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.permissions import require_permission
from utils.auth import get_current_user_id
from db import get_db
from schemas.schemas import CreateProject, UpdateProject

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/")
async def list_projects(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Менеджер и админ могут читать проекты, обычный пользователь — нет
    await require_permission("projects:read", db, current_user_id)
    # Мок‑данные
    return [
        {"id": 1, "name": "Проект A", "status": "active"},
        {"id": 2, "name": "Проект B", "status": "inactive"},
    ]


@router.post("/")
async def create_project(
    project: CreateProject,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Менеджер и админ могут создавать проекты
    await require_permission("projects:write", db, current_user_id)
    # Мок: возвращаем "созданный" объект
    return {"id": 3, "name": project.name, "status": "active"}


@router.put("/{project_id}")
async def update_project(
    project: UpdateProject,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Менеджер и админ могут обновлять проекты
    await require_permission("projects:write", db, current_user_id)
    # Мок: возвращаем обновлённый объект
    return {
        "id": project.project_id,
        "name": project.name,
        "message": "Проект обновлён",
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Менеджер и админ могут удалять проекты
    await require_permission("projects:delete", db, current_user_id)
    # Мок: удаление логическое, без реальной записи в БД
    return {"message": f"Проект {project_id} удалён"}