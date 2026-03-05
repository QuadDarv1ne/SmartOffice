#!/usr/bin/env bash

# ============================================
# Скрипт валидации конфигурации деплоя
# ============================================
# Проверяет все конфигурационные файлы перед деплоем

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Валидация конфигурации деплоя SmartOffice..."
echo "================================================"

ERRORS=0
WARNINGS=0

# ============================================
# Проверка netlify.toml
# ============================================
echo -e "\n📋 Проверка netlify.toml..."
if [ -f "netlify.toml" ]; then
    echo -e "${GREEN}✓ netlify.toml найден${NC}"
    
    # Проверка синтаксиса TOML
    if command -v python3 &> /dev/null; then
        python3 -c "import tomllib; tomllib.load(open('netlify.toml', 'rb'))" 2>/dev/null || \
        python3 -c "import toml; toml.load('netlify.toml')" 2>/dev/null && \
        echo -e "${GREEN}✓ Синтаксис TOML валиден${NC}" || \
        echo -e "${YELLOW}⚠ Не удалось проверить синтаксис TOML (установите Python с tomllib)${NC}"
    fi
else
    echo -e "${RED}✗ netlify.toml не найден${NC}"
    ((ERRORS++))
fi

# ============================================
# Проверка wrangler.toml
# ============================================
echo -e "\n📋 Проверка wrangler.toml..."
if [ -f "wrangler.toml" ]; then
    echo -e "${GREEN}✓ wrangler.toml найден${NC}"
    
    # Проверка наличия обязательного поля name
    if grep -q "^name = " wrangler.toml; then
        echo -e "${GREEN}✓ Поле name найдено${NC}"
    else
        echo -e "${YELLOW}⚠ Поле name не найдено (рекомендуется добавить)${NC}"
        ((WARNINGS++))
    fi
    
    # Проверка compatibility_date
    if grep -q "^compatibility_date = " wrangler.toml; then
        echo -e "${GREEN}✓ compatibility_date найден${NC}"
    else
        echo -e "${YELLOW}⚠ compatibility_date не найден (рекомендуется добавить)${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗ wrangler.toml не найден${NC}"
    ((ERRORS++))
fi

# ============================================
# Проверка GitHub Actions workflow
# ============================================
echo -e "\n📋 Проверка .github/workflows/deploy.yml..."
if [ -f ".github/workflows/deploy.yml" ]; then
    echo -e "${GREEN}✓ deploy.yml найден${NC}"
    
    # Проверка наличия необходимых secrets
    if grep -q "NETLIFY_AUTH_TOKEN" .github/workflows/deploy.yml; then
        echo -e "${GREEN}✓ NETLIFY_AUTH_TOKEN настроен${NC}"
    fi
    
    if grep -q "CLOUDFLARE_API_TOKEN" .github/workflows/deploy.yml; then
        echo -e "${GREEN}✓ CLOUDFLARE_API_TOKEN настроен${NC}"
    fi
else
    echo -e "${RED}✗ .github/workflows/deploy.yml не найден${NC}"
    ((ERRORS++))
fi

# ============================================
# Проверка frontend/.env.example
# ============================================
echo -e "\n📋 Проверка frontend/.env.example..."
if [ -f "frontend/.env.example" ]; then
    echo -e "${GREEN}✓ frontend/.env.example найден${NC}"
    
    # Проверка наличия VITE_API_URL
    if grep -q "VITE_API_URL" frontend/.env.example; then
        echo -e "${GREEN}✓ VITE_API_URL настроен${NC}"
    else
        echo -e "${YELLOW}⚠ VITE_API_URL не найден${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗ frontend/.env.example не найден${NC}"
    ((ERRORS++))
fi

# ============================================
# Проверка package.json
# ============================================
echo -e "\n📋 Проверка frontend/package.json..."
if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✓ frontend/package.json найден${NC}"
    
    # Проверка наличия скрипта build
    if grep -q '"build"' frontend/package.json; then
        echo -e "${GREEN}✓ Скрипт build найден${NC}"
    else
        echo -e "${RED}✗ Скрипт build не найден в package.json${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗ frontend/package.json не найден${NC}"
    ((ERRORS++))
fi

# ============================================
# Проверка Node.js и npm
# ============================================
echo -e "\n📋 Проверка окружения..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓ Node.js: ${NODE_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ Node.js не найден (требуется для локального билда)${NC}"
    ((WARNINGS++))
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo -e "${GREEN}✓ npm: ${NPM_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ npm не найден${NC}"
    ((WARNINGS++))
fi

# ============================================
# Итоги
# ============================================
echo -e "\n================================================"
echo -e "Результаты валидации:"
echo -e "  ${GREEN}✓ Успешно${NC}: $((8 - ERRORS - WARNINGS))"
echo -e "  ${YELLOW}⚠ Предупреждения${NC}: ${WARNINGS}"
echo -e "  ${RED}✗ Ошибки${NC}: ${ERRORS}"
echo "================================================"

if [ $ERRORS -gt 0 ]; then
    echo -e "\n${RED}❌ Обнаружены ошибки! Устраните их перед деплоем.${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  Обнаружены предупреждения. Рекомендуется проверить.${NC}"
    exit 0
else
    echo -e "\n${GREEN}✅ Все проверки пройдены! Можно деплоить.${NC}"
    exit 0
fi
