-- ============================================
-- Файл: 05_insert_test_data.sql
-- Назначение: наполнение базы тестовыми данными (расширенная версия)
-- ============================================

-- Очистка данных (если нужно перезаполнить)
-- TRUNCATE ... CASCADE;

-- Должности
INSERT INTO positions (title, min_salary, max_salary) VALUES
    ('Генеральный директор', 300000, 600000),
    ('Технический директор', 250000, 500000),
    ('Руководитель отдела разработки', 200000, 400000),
    ('Ведущий разработчик', 150000, 300000),
    ('Разработчик', 80000, 200000),
    ('Менеджер по продажам', 50000, 200000),
    ('Бухгалтер', 60000, 150000),
    ('HR-менеджер', 50000, 150000),
    ('Системный администратор', 70000, 180000);

-- Отделы
INSERT INTO departments (name) VALUES 
    ('Администрация'),
    ('Разработка'),
    ('Продажи'),
    ('Бухгалтерия'),
    ('HR');

-- Поставщики
INSERT INTO suppliers (name, contact_person, phone, email) VALUES
    ('ООО "Компьютерный мир"', 'Иван Петров', '+7 (495) 123-45-67', 'info@compworld.ru'),
    ('АО "Техносити"', 'Мария Сидорова', '+7 (495) 765-43-21', 'sales@techcity.ru');

-- Графики работы
INSERT INTO work_schedules (name, description, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_time, end_time) VALUES
    ('5/2 (9-18)', 'Стандартная пятидневка', true, true, true, true, true, false, false, '09:00', '18:00'),
    ('5/2 (10-19)', 'Пятидневка со смещением', true, true, true, true, true, false, false, '10:00', '19:00'),
    ('2/2 (9-21)', 'Сменный график 2 через 2', true, true, false, false, true, true, false, '09:00', '21:00');

-- Сотрудники (без руководителей, потом обновим)
INSERT INTO employees (full_name, email, hire_date, department_id, position_id, schedule_id) VALUES
    ('Александров Александр', 'a.alexandrov@smartoffice.ru', '2018-02-10', 1, 1, 1),
    ('Борисов Борис', 'b.borisov@smartoffice.ru', '2019-05-15', 2, 2, 1),
    ('Викторова Виктория', 'v.viktorova@smartoffice.ru', '2020-03-20', 2, 3, 1),
    ('Григорьев Григорий', 'g.grigoriev@smartoffice.ru', '2021-07-01', 2, 4, 2),
    ('Дмитриева Дарья', 'd.dmitrieva@smartoffice.ru', '2021-09-12', 2, 5, 2),
    ('Евгеньев Евгений', 'e.evgenev@smartoffice.ru', '2022-01-17', 3, 6, 1),
    ('Жукова Жанна', 'j.zhukova@smartoffice.ru', '2020-11-22', 4, 7, 1),
    ('Зайцев Захар', 'z.zaytsev@smartoffice.ru', '2023-04-05', 5, 8, 1),
    ('Ильина Ирина', 'i.ilina@smartoffice.ru', '2022-08-30', 2, 5, 2),
    ('Козлов Кирилл', 'k.kozlov@smartoffice.ru', '2023-01-09', 2, 5, 2);

-- Обновляем руководителей отделов (manager_id)
UPDATE departments SET manager_id = 1 WHERE department_id = 1;
UPDATE departments SET manager_id = 2 WHERE department_id = 2;
UPDATE departments SET manager_id = 6 WHERE department_id = 3;
UPDATE departments SET manager_id = 7 WHERE department_id = 4;
UPDATE departments SET manager_id = 8 WHERE department_id = 5;

-- Обновляем руководителей (manager_id) для сотрудников
UPDATE employees SET manager_id = 1 WHERE employee_id IN (2,6,7,8);
UPDATE employees SET manager_id = 2 WHERE employee_id IN (3,4,5,9,10);
UPDATE employees SET manager_id = 3 WHERE employee_id IN (4,9); -- пример

-- Адреса сотрудников
INSERT INTO employee_addresses (employee_id, address_type, city, street, house, apartment, valid_from) VALUES
    (1, 'registration', 'Москва', 'Тверская', '10', '25', '2018-02-10'),
    (1, 'residential', 'Москва', 'Арбат', '5', '12', '2020-01-01'),
    (2, 'registration', 'Санкт-Петербург', 'Невский проспект', '20', '5', '2019-05-15');

-- Члены семьи
INSERT INTO family_members (employee_id, full_name, relationship, birth_date, is_dependent) VALUES
    (1, 'Александрова Анна', 'spouse', '1985-03-12', false),
    (1, 'Александров Петр', 'child', '2010-07-21', true),
    (2, 'Борисова Елена', 'spouse', '1990-11-05', false);

-- Банковские реквизиты
INSERT INTO employee_bank_details (employee_id, bank_name, bik, account_number, correspondent_account, is_default) VALUES
    (1, 'Сбербанк', '044525225', '40817810000000000001', '30101810400000000225', true),
    (2, 'ВТБ', '044525743', '40817810000000000002', '30101810700000000743', true);

-- Проекты
INSERT INTO projects (name, description, start_date, status, manager_id, budget) VALUES
    ('Внедрение CRM', 'Проект по внедрению корпоративной CRM-системы', '2024-01-15', 'active', 3, 2000000),
    ('Разработка мобильного приложения', 'Создание мобильного приложения для клиентов', '2024-03-01', 'active', 4, 3500000),
    ('Миграция серверов', 'Перенос серверной инфраструктуры в облако', '2024-02-10', 'completed', 9, 1500000);

-- Задачи
INSERT INTO tasks (project_id, title, assigned_to, deadline, status, priority, estimated_hours) VALUES
    (1, 'Сбор требований к CRM', 4, '2024-02-01', 'completed', 'high', 40),
    (1, 'Выбор платформы', 3, '2024-02-15', 'completed', 'high', 20),
    (1, 'Настройка интеграции с 1С', 5, '2024-03-10', 'in_progress', 'medium', 80),
    (2, 'Дизайн интерфейса', 9, '2024-04-01', 'new', 'medium', 60),
    (2, 'Разработка бэкенда', 4, '2024-05-01', 'new', 'high', 120),
    (3, 'Резервное копирование данных', 10, '2024-02-20', 'completed', 'low', 10);

-- Участники проектов
INSERT INTO project_team (project_id, employee_id, role) VALUES
    (1, 3, 'Руководитель проекта'),
    (1, 4, 'Аналитик'),
    (1, 5, 'Разработчик'),
    (2, 4, 'Архитектор'),
    (2, 9, 'Дизайнер'),
    (2, 5, 'Разработчик'),
    (3, 9, 'Системный администратор'),
    (3, 10, 'Системный администратор');

-- Оклады
INSERT INTO salaries (employee_id, effective_date, amount) VALUES
    (1, '2018-02-10', 400000),
    (2, '2019-05-15', 280000),
    (3, '2020-03-20', 220000),
    (4, '2021-07-01', 180000),
    (5, '2021-09-12', 120000),
    (6, '2022-01-17', 150000),
    (7, '2020-11-22', 110000),
    (8, '2023-04-05', 90000),
    (9, '2022-08-30', 130000),
    (10, '2023-01-09', 125000);

-- Начисления (за последний месяц)
INSERT INTO payroll (employee_id, period_start, period_end, base_salary, bonus, deductions, payment_date) VALUES
    (1, '2024-02-01', '2024-02-29', 400000, 100000, 50000, '2024-03-05'),
    (2, '2024-02-01', '2024-02-29', 280000, 50000, 30000, '2024-03-05'),
    (3, '2024-02-01', '2024-02-29', 220000, 40000, 25000, '2024-03-05'),
    (4, '2024-02-01', '2024-02-29', 180000, 30000, 20000, '2024-03-05'),
    (5, '2024-02-01', '2024-02-29', 120000, 20000, 15000, '2024-03-05');

-- Оборудование
INSERT INTO assets (name, type, serial_number, supplier_id, purchase_date, purchase_price, warranty_until, status) VALUES
    ('Ноутбук Dell XPS 15', 'Ноутбук', 'SN-DELL-001', 1, '2023-05-10', 150000, '2025-05-10', 'assigned'),
    ('Ноутбук MacBook Pro 14"', 'Ноутбук', 'SN-APPLE-002', 1, '2023-06-20', 250000, '2025-06-20', 'assigned'),
    ('Монитор LG 27"', 'Монитор', 'SN-LG-003', 2, '2023-04-15', 30000, '2025-04-15', 'available'),
    ('Клавиатура Logitech', 'Периферия', 'SN-LOG-004', 2, '2023-07-01', 5000, '2025-07-01', 'assigned'),
    ('Мышь Logitech', 'Периферия', 'SN-LOG-005', 2, '2023-07-01', 3000, '2025-07-01', 'assigned');

-- Выдача оборудования
INSERT INTO asset_assignments (asset_id, employee_id, assigned_date) VALUES
    (1, 4, '2023-05-15'),
    (2, 3, '2023-06-25'),
    (4, 5, '2023-07-05'),
    (5, 6, '2023-07-05');

-- Курсы
INSERT INTO courses (title, provider, duration_hours) VALUES
    ('PostgreSQL для администраторов', 'Postgres Professional', 40),
    ('Управление IT-проектами', 'Нетология', 72),
    ('Английский для IT', 'Skyeng', 60);

-- Сертификаты
INSERT INTO certificates (employee_id, course_id, issue_date, grade) VALUES
    (3, 1, '2023-12-10', 'Отлично'),
    (4, 2, '2023-11-20', 'Хорошо'),
    (9, 3, '2024-01-15', 'C1');

-- Навыки
INSERT INTO skills (name, category) VALUES
    ('SQL', 'Базы данных'),
    ('Python', 'Разработка'),
    ('JavaScript', 'Разработка'),
    ('Управление проектами', 'Менеджмент'),
    ('Английский язык', 'Языки');

-- Навыки сотрудников
INSERT INTO employee_skills (employee_id, skill_id, level) VALUES
    (3, 1, 5), (3, 2, 4), (3, 4, 5),
    (4, 1, 5), (4, 2, 5), (4, 3, 3),
    (5, 1, 4), (5, 2, 3),
    (9, 5, 4);

-- Кандидаты
INSERT INTO candidates (full_name, email, position_applied, status, resume_text) VALUES
    ('Смирнов Сергей', 's.smirnov@example.com', 5, 'new', 'Опытный разработчик с знанием Java, Spring, PostgreSQL...'),
    ('Кузнецова Ольга', 'o.kuznetsova@example.com', 6, 'interviewed', 'Менеджер по продажам, опыт 5 лет...');

-- Интервью
INSERT INTO interviews (candidate_id, employee_id, interview_date, feedback, rating, status) VALUES
    (2, 6, '2024-03-10 14:00:00', 'Хорошее впечатление, уверенные знания', 8, 'completed');

-- KPI периоды
INSERT INTO kpi_periods (name, start_date, end_date) VALUES
    ('1 квартал 2024', '2024-01-01', '2024-03-31');

-- KPI показатели
INSERT INTO kpi_indicators (name, unit, target_value, weight) VALUES
    ('Выполнение плана продаж', '%', 100, 50),
    ('Количество новых клиентов', 'шт.', 10, 30),
    ('Удовлетворённость клиентов', 'балл', 4.5, 20);

-- KPI результаты (пример для Евгеньева)
INSERT INTO employee_kpi_results (employee_id, period_id, indicator_id, actual_value, score) VALUES
    (6, 1, 1, 95, 47.5),
    (6, 1, 2, 8, 24),
    (6, 1, 3, 4.7, 20);

-- Командировки
INSERT INTO business_trips (employee_id, destination, start_date, end_date, purpose, status) VALUES
    (4, 'Санкт-Петербург', '2024-04-10', '2024-04-12', 'Встреча с заказчиком', 'planned'),
    (9, 'Казань', '2024-03-20', '2024-03-22', 'Настройка оборудования', 'completed');

-- Документы (просто пример)
INSERT INTO documents (file_name, file_path, document_type) VALUES
    ('passport_ivanov.pdf', '/docs/passports/ivanov.pdf', 'passport'),
    ('diplom_petrov.pdf', '/docs/diplomas/petrov.pdf', 'diploma');

-- Связь документов с сотрудниками
INSERT INTO employee_documents (employee_id, document_id) VALUES
    (1, 1),
    (2, 2);