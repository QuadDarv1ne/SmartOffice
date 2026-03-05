# ============================================
# Скрипт для локального тестирования production сборки (PowerShell)
# ============================================
# Собирает frontend и запускает preview сервер

$ErrorActionPreference = "Stop"

Write-Host "🔨 Сборка frontend для production..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Set-Location frontend

# Проверка наличия .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env не найден. Копируем из .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠ Отредактируйте frontend/.env и установите VITE_API_URL" -ForegroundColor Yellow
}

# Установка зависимостей
Write-Host "`n📦 Установка зависимостей..." -ForegroundColor Yellow
npm ci

# Сборка
Write-Host "`n🏗  Сборка production версии..." -ForegroundColor Yellow
npm run build

Write-Host "`n✅ Сборка завершена!" -ForegroundColor Green
Write-Host "📁 Директория сборки: frontend/dist"

# Предзапуск preview сервера
Write-Host "`n🚀 Запуск preview сервера..." -ForegroundColor Cyan
Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Yellow

npm run preview -- --port 4173 --host
