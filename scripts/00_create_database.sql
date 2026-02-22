-- ============================================
-- Файл: 00_create_database.sql
-- Назначение: создание базы данных SmartOffice (улучшенная версия)
-- ============================================

-- Важно: выполнять под суперпользователем или пользователем с правом создания БД
CREATE DATABASE SmartOffice
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8'
    TEMPLATE = template0;

-- Подключение к созданной базе (выполнить отдельно)
-- \c SmartOffice;