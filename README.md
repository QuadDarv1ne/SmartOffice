# SmartOffice

> Умный офис — комплексная система управления корпоративными ресурсами

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)](https://www.postgresql.org/)

**Цель проекта:** создание единой платформы для учета кадров, управления задачами, складским хозяйством и другими аспектами работы современного офиса.

---

## 📋 Оглавление

- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Быстрый старт](#-быстрый-старт)
- [Разработка](#-разработка)
- [API Документация](#-api-документация)
- [Структура проекта](#-структура-проекта)
- [Вклад](#-вклад)
- [Лицензия](#-лицензия)

---

## ✨ Возможности

| Модуль | Описание |
|--------|----------|
| 👥 **HRM** | Учёт сотрудников, отделов, должностей |
| 📅 **TAM** | Учёт рабочего времени, отпуска, больничные |
| 📊 **PMS** | Управление проектами и задачами |
| 📦 **IMS** | Складской учёт оборудования |
| 🎯 **KPI** | Оценка эффективности сотрудников |
| 🎓 **LMS** | Обучение и сертификация |

---

## 🛠 Технологии

### Backend

- **FastAPI** 0.109 — современный веб-фреймворк
- **SQLAlchemy 2.0** — ORM с асинхронной поддержкой
- **PostgreSQL 15** — реляционная база данных
- **Pydantic** — валидация данных
- **JWT** — аутентификация

### Frontend

- **React 18** — UI-библиотека
- **TypeScript 5** — типизация
- **Vite 5** — сборщик
- **React Router 6** — навигация
- **Bootstrap 5** — компоненты UI
- **Axios** — HTTP-клиент

### DevOps

- **Docker & Docker Compose** — контейнеризация
- **Alembic** — миграции БД

---

## Быстрый старт

### Требования

- Docker & Docker Compose
- Node.js 20+ (для локальной разработки frontend)
- Python 3.11+ (для локальной разработки backend)

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/SmartOffice.git
cd SmartOffice
```

### 2. Настройка переменных окружения

```bash
# Скопируйте примеры файлов окружения
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Отредактируйте backend/.env и установите SECRET_KEY
# Сгенерируйте ключ: openssl rand -hex 32
```

### 3. Запуск через Docker

```bash
docker-compose up --build
```

**После запуска:**

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

### 4. Остановка

```bash
docker-compose down
```

---

## 💻 Разработка

### Backend (локально)

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
cp .env.example .env

# Запуск
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (локально)

```bash
cd frontend

# Установка зависимостей
npm install

# Копирование .env
cp .env.example .env

# Запуск
npm run dev
```

---

## 📚 API Документация

После запуска backend доступны:

| Документация | URL |
|--------------|-----|
| Swagger UI | http://localhost:8000/api/docs |
| ReDoc | http://localhost:8000/api/redoc |
| OpenAPI JSON | http://localhost:8000/api/openapi.json |

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход в систему |
| GET | `/api/employees` | Список сотрудников |
| POST | `/api/employees` | Создание сотрудника |
| GET | `/api/departments` | Список отделов |
| GET | `/api/projects` | Список проектов |
| GET | `/api/tasks` | Список задач |
| GET | `/api/assets` | Список оборудования |

---

## 📁 Структура проекта

```
SmartOffice/
├── .env.example              # Шаблон переменных окружения
├── docker-compose.yml        # Docker конфигурация
├── README.md                 # Документация
├── LICENCE                   # Лицензия MIT
│
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── main.py           # Точка входа
│       ├── core/             # Конфигурация, БД, безопасность
│       ├── models/           # SQLAlchemy модели
│       ├── schemas/          # Pydantic схемы
│       ├── api/              # API роутеры
│       └── services/         # Бизнес-логика
│
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── App.tsx           # Главный компонент
│       ├── main.tsx          # Точка входа
│       ├── api/              # API клиенты
│       ├── components/       # UI компоненты
│       ├── pages/            # Страницы
│       └── store/            # State management
│
└── scripts/
    ├── 00_create_database.sql
    ├── 01_create_tables.sql
    ├── 02_add_constraints.sql
    ├── 03_create_indexes.sql
    ├── 04_create_triggers.sql
    ├── 05_insert_test_data.sql
    └── 06_views.sql
```

---

## 🤝 Вклад

Проект открыт для вкладов! Для участия:

1. Создайте форк репозитория
2. Создайте ветку для фичи: `git checkout -b feature/AmazingFeature`
3. Закоммитьте изменения: `git commit -m 'Add AmazingFeature'`
4. Отправьте в ветку: `git push origin feature/AmazingFeature`
5. Откройте Pull Request

### Стандарты кода

- **Backend:** black, ruff, mypy
- **Frontend:** ESLint, Prettier, TypeScript strict

---

## 📄 Лицензия

Этот проект лицензирован по лицензии MIT. См. файл [LICENCE](LICENCE) для деталей.

---

## 📞 Контакты

**Для вопросов и предложений:**

- GitHub Issues: [Создать issue](https://github.com/yourusername/SmartOffice/issues)

---

## 📈 Roadmap

- [ ] Unit-тесты (pytest, vitest)
- [ ] CI/CD (GitHub Actions)
- [ ] Production Docker (nginx)
- [ ] Логирование (structlog)
- [ ] Rate limiting
- [ ] WebSocket уведомления
- [ ] Мобильное приложение

---

*Создано с ❤️ для умных офисов*
