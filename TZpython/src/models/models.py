from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    surname = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    hash_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    #Связи
    roles = relationship("Roles", secondary=user_roles, back_populates="users")


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # 'admin', 'user', 'moderator'
    description = Column(String(255))

    # Связи
    users = relationship("Users", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permissions", secondary=role_permissions, back_populates="roles")


class Permissions(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # 'users:read', 'users:write', 'admin:manage'
    description = Column(String(255))
    resource = Column(String(50))  # 'users', 'orders', 'admin'

    # Связи
    roles = relationship("Roles", secondary=role_permissions, back_populates="permissions")