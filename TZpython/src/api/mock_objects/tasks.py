from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.permissions import require_permission
from utils.auth import get_current_user_id
from db import get_db
from schemas.schemas import CreateTasks

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])

@router.get("/")
async def list_tasks(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await require_permission("projects:read", db, current_user_id)
    # Мок‑данные
    return [
        {"id": 101, "project_id": project_id, "title": "Сделать прототип", "status": "open"},
        {"id": 102, "project_id": project_id, "title": "Написать документацию", "status": "closed"},
    ]


@router.post("/")
async def create_task(
    task: CreateTasks,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await require_permission("projects:write", db, current_user_id)
    return {"id": 103, "project_id": task.project_id, "status": "open"}