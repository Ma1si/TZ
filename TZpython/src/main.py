from fastapi import FastAPI
import asyncio
import uvicorn
from db import create_table
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth
from api.user import router as user
from api.admin import router as admin
from api.roles import router as role
from api.permission import router as permission
from api.mock_objects.projects import router as mock_projects
from api.mock_objects.reports import router as mock_reports
from api.mock_objects.tasks import router as mock_tasks


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # разрешить любой origin
    allow_credentials=False,       # иначе * недопустимо
    allow_methods=["*"],           # все методы
    allow_headers=["*"],           # все заголовки
)

@app.get('/')
def root():
    return 'hello world'

app.include_router(auth)
app.include_router(user)
app.include_router(admin)
app.include_router(role)
app.include_router(permission)
app.include_router(mock_projects)
app.include_router(mock_reports)
app.include_router(mock_tasks)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)