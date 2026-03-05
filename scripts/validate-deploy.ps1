# ============================================
# Скрипт валидации конфигурации деплоя (PowerShell)
# ============================================
# Проверяет все конфигурационные файлы перед деплоем

$ErrorActionPreference = "Continue"

Write-Host "🔍 Валидация конфигурации деплоя SmartOffice..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$Errors = 0
$Warnings = 0

# ============================================
# Проверка netlify.toml
# ============================================
Write-Host "`n📋 Проверка netlify.toml..." -ForegroundColor Yellow
if (Test-Path "netlify.toml") {
    Write-Host "✓ netlify.toml найден" -ForegroundColor Green
} else {
    Write-Host "✗ netlify.toml не найден" -ForegroundColor Red
    $Errors++
}

# ============================================
# Проверка wrangler.toml
# ============================================
Write-Host "`n📋 Проверка wrangler.toml..." -ForegroundColor Yellow
if (Test-Path "wrangler.toml") {
    Write-Host "✓ wrangler.toml найден" -ForegroundColor Green
    
    $Content = Get-Content "wrangler.toml" -Raw
    
    if ($Content -match "^name\s*=") {
        Write-Host "✓ Поле name найдено" -ForegroundColor Green
    } else {
        Write-Host "⚠ Поле name не найдено (рекомендуется добавить)" -ForegroundColor Yellow
        $Warnings++
    }
    
    if ($Content -match "^compatibility_date\s*=") {
        Write-Host "✓ compatibility_date найден" -ForegroundColor Green
    } else {
        Write-Host "⚠ compatibility_date не найден (рекомендуется добавить)" -ForegroundColor Yellow
        $Warnings++
    }
} else {
    Write-Host "✗ wrangler.toml не найден" -ForegroundColor Red
    $Errors++
}

# ============================================
# Проверка GitHub Actions workflow
# ============================================
Write-Host "`n📋 Проверка .github/workflows/deploy.yml..." -ForegroundColor Yellow
if (Test-Path ".github/workflows/deploy.yml") {
    Write-Host "✓ deploy.yml найден" -ForegroundColor Green
} else {
    Write-Host "✗ .github/workflows/deploy.yml не найден" -ForegroundColor Red
    $Errors++
}

# ============================================
# Проверка frontend/.env.example
# ============================================
Write-Host "`n📋 Проверка frontend/.env.example..." -ForegroundColor Yellow
if (Test-Path "frontend/.env.example") {
    Write-Host "✓ frontend/.env.example найден" -ForegroundColor Green
    
    $Content = Get-Content "frontend/.env.example" -Raw
    if ($Content -match "VITE_API_URL") {
        Write-Host "✓ VITE_API_URL настроен" -ForegroundColor Green
    } else {
        Write-Host "⚠ VITE_API_URL не найден" -ForegroundColor Yellow
        $Warnings++
    }
} else {
    Write-Host "✗ frontend/.env.example не найден" -ForegroundColor Red
    $Errors++
}

# ============================================
# Проверка package.json
# ============================================
Write-Host "`n📋 Проверка frontend/package.json..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "✓ frontend/package.json найден" -ForegroundColor Green
    
    $Content = Get-Content "frontend/package.json" -Raw
    if ($Content -match '"build"') {
        Write-Host "✓ Скрипт build найден" -ForegroundColor Green
    } else {
        Write-Host "✗ Скрипт build не найден в package.json" -ForegroundColor Red
        $Errors++
    }
} else {
    Write-Host "✗ frontend/package.json не найден" -ForegroundColor Red
    $Errors++
}

# ============================================
# Проверка Node.js и npm
# ============================================
Write-Host "`n📋 Проверка окружения..." -ForegroundColor Yellow
try {
    $NodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $NodeVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Node.js не найден (требуется для локального билда)" -ForegroundColor Yellow
    $Warnings++
}

try {
    $NpmVersion = npm --version 2>&1
    Write-Host "✓ npm: $NpmVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ npm не найден" -ForegroundColor Yellow
    $Warnings++
}

# ============================================
# Итоги
# ============================================
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Результаты валидации:" -ForegroundColor Cyan
Write-Host "  ✓ Успешно: $((8 - $Errors - $Warnings))" -ForegroundColor Green
Write-Host "  ⚠ Предупреждения: $Warnings" -ForegroundColor Yellow
Write-Host "  ✗ Ошибки: $Errors" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Cyan

if ($Errors -gt 0) {
    Write-Host "`n❌ Обнаружены ошибки! Устраните их перед деплоем." -ForegroundColor Red
    exit 1
} elseif ($Warnings -gt 0) {
    Write-Host "`n⚠️  Обнаружены предупреждения. Рекомендуется проверить." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n✅ Все проверки пройдены! Можно деплоить." -ForegroundColor Green
    exit 0
}
