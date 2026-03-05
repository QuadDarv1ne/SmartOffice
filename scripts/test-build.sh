#!/usr/bin/env bash

# ============================================
# Скрипт для локального тестирования production сборки
# ============================================
# Собирает frontend и запускает preview сервер

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔨 Сборка frontend для production..."
echo "====================================="

cd frontend

# Проверка наличия .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env не найден. Копируем из .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Отредактируйте frontend/.env и установите VITE_API_URL${NC}"
fi

# Установка зависимостей
echo -e "\n📦 Установка зависимостей..."
npm ci

# Сборка
echo -e "\n🏗  Сборка production версии..."
npm run build

echo -e "\n${GREEN}✅ Сборка завершена!${NC}"
echo -e "📁 Директория сборки: frontend/dist"

# Предзапуск preview сервера
echo -e "\n🚀 Запуск preview сервера..."
echo -e "${YELLOW}Нажмите Ctrl+C для остановки${NC}"

npm run preview -- --port 4173 --host
