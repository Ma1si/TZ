import asyncio
from sqlalchemy import select, insert
from db import AsyncSessionLocal, engine
from models.models import Permissions, Roles, Users, user_roles, Base
from utils.auth import hash_password

async def init_rbac():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn))

    async with AsyncSessionLocal() as db:
        stmt = select(Permissions.id)
        result = await db.execute(stmt)
        if not result.scalar():
            perms_data = [
                {"name": "users:read", "description": "Чтение пользователей", "resource": "users"},
                {"name": "users:write", "description": "Изменение пользователей", "resource": "users"},
                {"name": "users:delete", "description": "Удаление пользователей", "resource": "users"},
                {"name": "admin:manage", "description": "Управление системой", "resource": "admin"},
                {"name": "projects:read", "description": "Чтение проектов", "resource": "projects"},
                {"name": "projects:write", "description": "Изменение проектов", "resource": "projects"},
                {"name": "projects:delete", "description": "Удаление проектов", "resource": "projects"},
            ]
            for data in perms_data:
                db.add(Permissions(**data))
            await db.commit()

        # 2. Получаем ВСЕ разрешения
        stmt = select(Permissions)
        result = await db.execute(stmt)
        all_perms = result.scalars().all()

        # Безопасно получаем разрешения
        users_read = next((p for p in all_perms if p.name == "users:read"), None)
        users_write = next((p for p in all_perms if p.name == "users:write"), None)
        users_delete = next((p for p in all_perms if p.name == "users:delete"), None)
        projects_read = next((p for p in all_perms if p.name == "projects:read"), None)
        projects_write = next((p for p in all_perms if p.name == "projects:write"), None)
        projects_delete = next((p for p in all_perms if p.name == "projects:delete"), None)

        # 3. Создаем роли
        stmt = select(Roles.id)
        result = await db.execute(stmt)
        if not result.scalar():
            admin_role = Roles(name="admin", description="Полный доступ")
            manager_role = Roles(name="manager", description="Чтение, изменение и удаление пользователей + проекты")
            user_role = Roles(name="user", description="Обычный пользователь")

            admin_role.permissions = all_perms
            manager_role.permissions = [
                users_read, users_write, users_delete,
                projects_read, projects_write, projects_delete,
            ]
            user_role.permissions = [users_read]

            db.add_all([admin_role, manager_role, user_role])
            await db.commit()
        else:
            # Если роли есть, загружаем их
            stmt = select(Roles).where(Roles.name.in_(["admin", "manager", "user"]))
            result = await db.execute(stmt)
            roles_dict = {role.name: role for role in result.scalars().all()}
            admin_role = roles_dict.get("admin")
            manager_role = roles_dict.get("manager")
            user_role = roles_dict.get("user")

        # 4. Создаем роли пользователям
        admin_email = "admin@example.com"
        manager_email = "manager@example.com"
        user_email = "user@example.com"

        # Создаем admin пользователя
        stmt = select(Users.id).where(Users.email == admin_email)
        result = await db.execute(stmt)
        admin_user_id = result.scalar()
        if not admin_user_id:
            admin_user = Users(
                first_name="Admin",
                last_name="Adminov",
                surname="Adminovich",
                email=admin_email,
                hash_password=hash_password("admin123"),
                is_active=True
            )
            db.add(admin_user)
            await db.commit()
            admin_user_id = admin_user.id

        # Назначаем роль admin
        stmt = insert(user_roles).values(user_id=admin_user_id, role_id=admin_role.id)
        await db.execute(stmt)
        await db.commit()

        # Проверяем/создаем manager пользователя
        stmt = select(Users.id).where(Users.email == manager_email)
        result = await db.execute(stmt)
        manager_user_id = result.scalar()
        if not manager_user_id:
            manager_user = Users(
                first_name="Manager",
                last_name="Managrov",
                surname="Managerovich",
                email=manager_email,
                hash_password=hash_password("manager123"),
                is_active=True
            )
            db.add(manager_user)
            await db.commit()
            manager_user_id = manager_user.id

        # Назначаем роль manager
        stmt = insert(user_roles).values(user_id=manager_user_id, role_id=manager_role.id)
        await db.execute(stmt)
        await db.commit()

        # Проверяем/создаем обычного пользователя
        stmt = select(Users.id).where(Users.email == user_email)
        result = await db.execute(stmt)
        test_user_id = result.scalar()
        if not test_user_id:
            test_user_obj = Users(
                first_name="Test",
                last_name="User",
                surname="Testovich",
                email=user_email,
                hash_password=hash_password("user123"),
                is_active=True
            )
            db.add(test_user_obj)
            await db.commit()
            test_user_id = test_user_obj.id

        # Назначаем роль user
        stmt = insert(user_roles).values(user_id=test_user_id, role_id=user_role.id)
        await db.execute(stmt)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(init_rbac())