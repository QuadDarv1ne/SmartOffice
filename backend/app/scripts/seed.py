"""
Seed скрипт для наполнения базы данных тестовыми данными

Использование:
    python -m app.scripts.seed

Требует запущенной базы данных PostgreSQL
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.employee import Department, Position, Employee
from app.models.project import Project
from app.models.asset import Asset
import structlog

logger = structlog.get_logger("smartoffice")


async def seed_database():
    """Наполнение базы данных тестовыми данными"""
    
    # Создаем engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("+asyncpg", "+asyncpg"),
        echo=False,
    )
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")
    
    async with async_session() as session:
        # Проверяем, есть ли уже данные
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            logger.info("Database already has data, skipping seed")
            return
        
        # === Создаем пользователей ===
        admin_user = User(
            email="admin@smartoffice.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True,
        )
        
        user1 = User(
            email="john.doe@smartoffice.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=False,
        )
        
        user2 = User(
            email="jane.smith@smartoffice.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=False,
        )
        
        session.add_all([admin_user, user1, user2])
        await session.commit()
        
        logger.info("Users created", count=3)
        
        # === Создаем отделы ===
        it_dept = Department(name="IT отдел")
        hr_dept = Department(name="HR отдел")
        sales_dept = Department(name="Отдел продаж")
        finance_dept = Department(name="Финансовый отдел")
        
        session.add_all([it_dept, hr_dept, sales_dept, finance_dept])
        await session.commit()
        
        logger.info("Departments created", count=4)
        
        # === Создаем должности ===
        positions = [
            Position(title="Разработчик", min_salary=80000, max_salary=150000),
            Position(title="Senior разработчик", min_salary=150000, max_salary=250000),
            Position(title="HR менеджер", min_salary=60000, max_salary=100000),
            Position(title="Менеджер по продажам", min_salary=50000, max_salary=120000),
            Position(title="Финансовый аналитик", min_salary=70000, max_salary=130000),
            Position(title="Team lead", min_salary=180000, max_salary=280000),
        ]
        
        session.add_all(positions)
        await session.commit()
        
        logger.info("Positions created", count=len(positions))
        
        # === Создаем сотрудников ===
        employees = [
            Employee(
                personnel_number="EMP001",
                full_name="Иванов Иван Иванович",
                email="ivanov@smartoffice.com",
                phone="+7 (999) 123-45-67",
                hire_date="2024-01-15",
                department_id=it_dept.department_id,
                position_id=positions[1].position_id,  # Senior разработчик
            ),
            Employee(
                personnel_number="EMP002",
                full_name="Петров Петр Петрович",
                email="petrov@smartoffice.com",
                phone="+7 (999) 234-56-78",
                hire_date="2024-03-01",
                department_id=it_dept.department_id,
                position_id=positions[0].position_id,  # Разработчик
            ),
            Employee(
                personnel_number="EMP003",
                full_name="Сидорова Анна Михайловна",
                email="sidorova@smartoffice.com",
                phone="+7 (999) 345-67-89",
                hire_date="2024-02-10",
                department_id=hr_dept.department_id,
                position_id=positions[2].position_id,  # HR менеджер
            ),
            Employee(
                personnel_number="EMP004",
                full_name="Козлов Дмитрий Александрович",
                email="kozlov@smartoffice.com",
                phone="+7 (999) 456-78-90",
                hire_date="2024-04-05",
                department_id=sales_dept.department_id,
                position_id=positions[3].position_id,  # Менеджер по продажам
            ),
            Employee(
                personnel_number="EMP005",
                full_name="Новикова Елена Сергеевна",
                email="novikova@smartoffice.com",
                phone="+7 (999) 567-89-01",
                hire_date="2024-01-20",
                department_id=finance_dept.department_id,
                position_id=positions[4].position_id,  # Финансовый аналитик
            ),
            Employee(
                personnel_number="EMP006",
                full_name="Морозов Алексей Владимирович",
                email="morozov@smartoffice.com",
                phone="+7 (999) 678-90-12",
                hire_date="2023-11-01",
                department_id=it_dept.department_id,
                position_id=positions[5].position_id,  # Team lead
                manager_id=None,
            ),
        ]
        
        # Устанавливаем менеджера для IT отдела
        it_dept.manager_id = employees[5].employee_id  # Team lead
        
        session.add_all(employees)
        await session.commit()
        
        logger.info("Employees created", count=len(employees))
        
        # === Создаем проекты ===
        projects = [
            Project(
                name="Разработка мобильного приложения",
                description="Создание мобильного приложения для учета рабочего времени",
                status="active",
                budget=500000,
            ),
            Project(
                name="Миграция на PostgreSQL",
                description="Переход с MySQL на PostgreSQL",
                status="completed",
                budget=200000,
            ),
            Project(
                name="Внедрение CRM",
                description="Настройка и внедрение CRM системы",
                status="active",
                budget=350000,
            ),
        ]
        
        session.add_all(projects)
        await session.commit()
        
        logger.info("Projects created", count=len(projects))
        
        # === Создаем оборудование ===
        assets = [
            Asset(
                name="MacBook Pro 16",
                type="Laptop",
                serial_number="MBP-2024-001",
                purchase_price=250000,
                status="assigned",
            ),
            Asset(
                name="Dell UltraSharp 27",
                type="Monitor",
                serial_number="DELL-2024-001",
                purchase_price=45000,
                status="available",
            ),
            Asset(
                name="iPhone 15 Pro",
                type="Smartphone",
                serial_number="IPH-2024-001",
                purchase_price=120000,
                status="assigned",
            ),
            Asset(
                name="Logitech MX Master 3",
                type="Mouse",
                serial_number="LOG-2024-001",
                purchase_price=10000,
                status="available",
            ),
        ]
        
        session.add_all(assets)
        await session.commit()
        
        logger.info("Assets created", count=len(assets))
        
        logger.info("=== Seed completed successfully ===")
    
    await engine.dispose()


if __name__ == "__main__":
    logger.info("Starting seed script...")
    asyncio.run(seed_database())
