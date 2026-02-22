# SmartOffice Makefile
# Автоматизация常见 задач разработки

.PHONY: help install dev backend frontend test lint clean docker seed

# Переменные
PYTHON ?= python
PIP ?= pip
NODE ?= node
NPM ?= npm
DOCKER ?= docker
DOCKER_COMPOSE ?= docker compose

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Показать эту справку
	@echo "$(BLUE)SmartOffice Makefile$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: install-backend install-frontend ## Установить все зависимости

install-backend: ## Установить зависимости backend
	@echo "$(YELLOW)Installing backend dependencies...$(NC)"
	cd backend && $(PIP) install -r requirements.txt

install-frontend: ## Установить зависимости frontend
	@echo "$(YELLOW)Installing frontend dependencies...$(NC)"
	cd frontend && $(NPM) install

install-dev: ## Установить dev зависимости
	@echo "$(YELLOW)Installing dev dependencies...$(NC)"
	cd backend && $(PIP) install -r requirements.txt
	cd backend && $(PIP) install pre-commit
	cd backend && pre-commit install

dev: ## Запустить разработку (backend + frontend)
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(MAKE) dev-backend &
	$(MAKE) dev-frontend

dev-backend: ## Запустить backend сервер
	@echo "$(GREEN)Starting backend server...$(NC)"
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Запустить frontend сервер
	@echo "$(GREEN)Starting frontend server...$(NC)"
	cd frontend && $(NPM) run dev

docker-up: ## Запустить Docker контейнеры (dev)
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	$(DOCKER_COMPOSE) up -d

docker-down: ## Остановить Docker контейнеры
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	$(DOCKER_COMPOSE) down

docker-prod-up: ## Запустить production Docker контейнеры
	@echo "$(GREEN)Starting production Docker containers...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d

docker-prod-down: ## Остановить production Docker контейнеры
	@echo "$(YELLOW)Stopping production Docker containers...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml down

docker-logs: ## Показать логи Docker контейнеров
	$(DOCKER_COMPOSE) logs -f

docker-restart: ## Перезапустить Docker контейнеры
	$(MAKE) docker-down
	$(MAKE) docker-up

test: test-backend test-frontend ## Запустить все тесты

test-backend: ## Запустить тесты backend
	@echo "$(YELLOW)Running backend tests...$(NC)"
	cd backend && $(PYTHON) -m pytest -v

test-backend-cov: ## Запустить тесты backend с coverage
	@echo "$(YELLOW)Running backend tests with coverage...$(NC)"
	cd backend && $(PYTHON) -m pytest -v --cov=app --cov-report=html

test-frontend: ## Запустить тесты frontend
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	cd frontend && $(NPM) test

lint: lint-backend lint-frontend ## Запустить линтеры

lint-backend: ## Линтинг backend
	@echo "$(YELLOW)Linting backend...$(NC)"
	cd backend && ruff check .
	cd backend && black --check .

lint-backend-fix: ## Линтинг backend с авто-исправлением
	@echo "$(GREEN)Fixing backend lint issues...$(NC)"
	cd backend && ruff check --fix .
	cd backend && black .

lint-frontend: ## Линтинг frontend
	@echo "$(YELLOW)Linting frontend...$(NC)"
	cd frontend && $(NPM) run lint || true

format: ## Форматировать код
	@echo "$(GREEN)Formatting code...$(NC)"
	cd backend && black .
	cd backend && ruff check --fix .

migrate: ## Создать миграцию Alembic
	@echo "$(YELLOW)Creating Alembic migration...$(NC)"
	cd backend && alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"

migrate-up: ## Применить все миграции
	@echo "$(YELLOW)Running migrations...$(NC)"
	cd backend && alembic upgrade head

migrate-down: ## Откатить последнюю миграцию
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	cd backend && alembic downgrade -1

seed: ## Наполнить БД тестовыми данными
	@echo "$(GREEN)Seeding database...$(NC)"
	cd backend && $(PYTHON) -m app.scripts.seed

backup: ## Создать backup базы данных
	@echo "$(GREEN)Creating database backup...$(NC)"
	cd backend && $(PYTHON) scripts/backup.py

backup-restore: ## Восстановить из последнего backup
	@echo "$(YELLOW)Restoring from latest backup...$(NC)"
	cd backend && $(PYTHON) scripts/backup.py --restore

backup-list: ## Показать список backup'ов
	@echo "$(BLUE)Available backups:$(NC)"
	cd backend && $(PYTHON) scripts/backup.py --list

backup-clean: ## Очистить старые backup'ы
	@echo "$(YELLOW)Cleaning old backups...$(NC)"
	cd backend && $(PYTHON) scripts/backup.py --clean

build: build-frontend ## Собрать проект

build-frontend: ## Собрать frontend
	@echo "$(YELLOW)Building frontend...$(NC)"
	cd frontend && $(NPM) run build

build-docker: ## Собрать Docker образы
	@echo "$(YELLOW)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build

clean: ## Очистить временные файлы
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	cd frontend && rm -rf node_modules dist build
	@echo "$(GREEN)Clean complete!$(NC)"

logs: ## Показать логи backend
	tail -f backend/logs/app.log

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)Setting up SmartOffice...$(NC)"
	cp .env.example .env
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	$(MAKE) install
	$(MAKE) docker-up
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:5173$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8000$(NC)"
	@echo "$(BLUE)API Docs: http://localhost:8000/api/docs$(NC)"
