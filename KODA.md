# KODA.md — Контекст проекта SmartOffice

## Обзор проекта

**SmartOffice** — комплексная система управления корпоративными ресурсами для среднего и крупного бизнеса. Платформа объединяет HR-модуль, управление проектами и задачами, учёт оборудования и финансовый контроль.

### Целевая аудитория

- HR-отдел
- Менеджеры проектов
- Администраторы офиса
- Руководители компании

---

## Технологический стек

### Backend

- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 (async)
- **База данных:** PostgreSQL 15
- **Аутентификация:** JWT (python-jose)
- **Валидация:** Pydantic v2
- **Миграции:** Alembic

### Frontend

- **Framework:** React 18 + TypeScript
- **Сборка:** Vite 5
- **UI:** Bootstrap 5 + React-Bootstrap
- **Маршрутизация:** React Router v6
- **HTTP-клиент:** Axios
- **Состояние:** React Query (TanStack Query) — *в процессе интеграции*

### Инфраструктура

- **Контейнеризация:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (планируется)

---

## Структура проекта

```textline
SmartOffice/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   │   ├── auth.py        # Аутентификация (JWT)
│   │   │   ├── employees.py   # CRUD сотрудников
│   │   │   ├── departments.py # CRUD отделов
│   │   │   ├── projects.py    # CRUD проектов
│   │   │   ├── tasks.py       # CRUD задач
│   │   │   ├── assets.py      # CRUD оборудования
│   │   │   └── dashboard.py   # Статистика для дашборда
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── core/              # Конфигурация, БД, безопасность
│   │   └── main.py            # Точка входа
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API-клиенты
│   │   ├── components/        # Переиспользуемые компоненты
│   │   ├── pages/             # Страницы приложения
│   │   ├── App.tsx            # Корневой компонент
│   │   └── main.tsx           # Точка входа
│   ├── package.json
│   └── Dockerfile
│
├── scripts/                    # SQL-скрипты инициализации БД
│   ├── 00_create_database.sql
│   ├── 01_create_tables.sql
│   ├── 02_add_constraints.sql
│   ├── 03_create_indexes.sql
│   ├── 04_create_triggers.sql
│   ├── 05_insert_test_data.sql
│   └── 06_views.sql
│
├── docker-compose.yml          # Оркестрация контейнеров
├── .env.example                # Шаблон переменных окружения
└── LICENCE                     # MIT License
```

---

## Сборка и запуск

### Предварительные требования

- Docker Desktop
- Node.js 20+ (для локальной разработки frontend)
- Python 3.11+ (для локальной разработки backend)

### Быстрый старт (Docker Compose)

```bash
# 1. Скопировать .env
cp .env.example .env

# 2. Запустить все сервисы
docker-compose up -d

# 3. Проверить статус
docker-compose ps
```

**URLs после запуска:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API документация (Swagger): http://localhost:8000/api/docs
- API документация (ReDoc): http://localhost:8000/api/redoc

### Локальная разработка

**Backend:**

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Сборка для продакшена

**Backend:**

```bash
docker build -t smartoffice-backend ./backend
```

**Frontend:**

```bash
cd frontend
npm run build  # Результат в dist/
```

---

## API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Авторизация (JWT) |
| POST | `/api/auth/token` | OAuth2 совместимый логин |

### Сотрудники

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/employees/` | Список сотрудников (пагинация, поиск) |
| GET | `/api/employees/{id}` | Получить сотрудника |
| POST | `/api/employees/` | Создать сотрудника |
| PUT | `/api/employees/{id}` | Обновить сотрудника |
| DELETE | `/api/employees/{id}` | Удалить сотрудника |

### Проекты и задачи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/projects/` | Список проектов |
| POST | `/api/projects/` | Создать проект |
| GET | `/api/tasks/` | Список задач |
| POST | `/api/tasks/` | Создать задачу |

### Оборудование

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/assets/` | Список оборудования |
| POST | `/api/assets/` | Добавить оборудование |
| POST | `/api/assets/{id}/assign` | Закрепить за сотрудником |
| POST | `/api/assets/{id}/return` | Вернуть на склад |

### Дашборд

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/dashboard/stats` | Общая статистика |
| GET | `/api/dashboard/employees-by-department` | Распределение по отделам |

---

## База данных

### Основные таблицы

- **employees** — Сотрудники
- **departments** — Отделы
- **positions** — Должности
- **projects** — Проекты
- **tasks** — Задачи
- **assets** — Оборудование
- **attendance** — Учёт рабочего времени
- **leave_requests** — Заявления на отпуск
- **salaries** — История окладов
- **payroll** — Расчётные листы

### Миграции

Для управления схемой БД используется `Alembic`

Файлы миграций должны находиться в `backend/alembic/versions/`

```bash
# Создать миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head
```

---

## Правила разработки

### Стиль кода

**Python (Backend):**

- Использовать type hints для всех функций
- Асинхронные функции для работы с БД
- Pydantic схемы для валидации входных/выходных данных
- Роуты в отдельных файлах в `app/api/`
- Модели SQLAlchemy в `app/models/`

**TypeScript (Frontend):**

- Строгая типизация (strict mode включён)
- API-клиенты в `src/api/`
- Компоненты в `src/components/`
- Страницы в `src/pages/`

### Безопасность

- **НИКОГДА** не коммитить `.env` файлы
- JWT токены хранятся в localStorage
- Секретный ключ должен быть минимум 32 символа
- В продакшене отключить `DEBUG=true`

### Коммиты

Использовать понятные сообщения:
- `feat: добавлена страница отчётов`
- `fix: исправлена ошибка авторизации`
- `refactor: оптимизация запросов к БД`

---

## Тестирование

### Backend (pytest)

```bash
cd backend
pytest
```

### Frontend (Jest)

```bash
cd frontend
npm test
```

---

## TODO / План развития

1. **Frontend:**
   - [ ] Интеграция React Query для кэширования
   - [ ] Валидация форм (react-hook-form + zod)
   - [ ] Уведомления (react-toastify)
   - [ ] Графики на дашборде (recharts)

2. **Backend:**
   - [ ] Настроить Alembic миграции
   - [ ] Добавить логирование
   - [ ] Rate limiting (slowapi)
   - [ ] Тесты (pytest + pytest-asyncio)

3. **Инфраструктура:**
   - [ ] CI/CD (GitHub Actions)
   - [ ] Nginx reverse proxy
   - [ ] Мониторинг (Prometheus + Grafana)

---

## Контакты

**Автор:** Dupley Maxim Igorevich

**Лицензия:** MIT
