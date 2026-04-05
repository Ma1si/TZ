from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    email: EmailStr
    password: str
    password_confirm: str

class UserLog(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    new_password: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str

class UserDelete(BaseModel):
    password : str

class PermissionCreate(BaseModel):
    name: str
    description: str
    resource: str

class PermissionOut(PermissionCreate):
    id: int

class RoleCreate(BaseModel):
    name: str
    description: str

class RoleOut(RoleCreate):
    id: int
    permissions: List[PermissionOut] = []

class RoleUpdate(BaseModel):
    roles: List[str]

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: Optional[str] = None

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    resource: Optional[str] = None

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None

class Permission(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    resource: Optional[str] = None

    class Config:
        from_attributes = True

class CreateProject(BaseModel):
    name: str
    description: str

class UpdateProject(BaseModel):
    project_id: int
    name: str
    description: str

class CreateTasks(BaseModel):
    project_id: int
    description: str