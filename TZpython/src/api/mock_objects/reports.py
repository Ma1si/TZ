from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.permissions import require_permission
from utils.auth import get_current_user_id
from db import get_db


router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/")
async def list_reports(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await require_permission("projects:read", db, current_user_id)
    return [
        {"id": 1, "title": "Отчёт за неделю 1", "period": "2026-04-01..2026-04-07"},
        {"id": 2, "title": "Отчёт за неделю 2", "period": "2026-04-08..2026-04-14"},
    ]


@router.get("/export")
async def export_report(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await require_permission("project:write", db, current_user_id)
    # Мок: возвращаем “ссылку” на файл
    return {"report_id": 1, "file_url": "/files/report_1.xlsx"}