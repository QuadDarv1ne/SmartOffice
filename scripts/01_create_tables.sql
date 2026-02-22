-- ============================================
-- Файл: 01_create_tables.sql
-- Назначение: создание всех таблиц базы данных SmartOffice (улучшенная версия)
-- ============================================

-- Включаем расширение для полнотекстового поиска (если не включено)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- 1. Справочники (независимые таблицы)
-- ============================================

-- Должности
CREATE TABLE positions (
    position_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL UNIQUE,
    min_salary DECIMAL(10,2),
    max_salary DECIMAL(10,2),
    CONSTRAINT salary_range_check CHECK (min_salary <= max_salary)
);
COMMENT ON TABLE positions IS 'Справочник должностей';

-- Отделы (без manager_id, добавим позже)
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    manager_id INTEGER,   -- будет добавлен внешний ключ позже
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE departments IS 'Отделы компании';

-- Поставщики оборудования
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    contact_person VARCHAR(150),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE suppliers IS 'Поставщики оборудования и материалов';

-- Навыки
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100)
);
COMMENT ON TABLE skills IS 'Справочник профессиональных навыков';

-- Курсы
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL UNIQUE,
    provider VARCHAR(200),
    duration_hours INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE courses IS 'Доступные обучающие курсы';

-- Графики работы (шаблоны)
CREATE TABLE work_schedules (
    schedule_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- например, "5/2 с 9 до 18", "сменный 2/2"
    description TEXT,
    monday BOOLEAN DEFAULT true,
    tuesday BOOLEAN DEFAULT true,
    wednesday BOOLEAN DEFAULT true,
    thursday BOOLEAN DEFAULT true,
    friday BOOLEAN DEFAULT true,
    saturday BOOLEAN DEFAULT false,
    sunday BOOLEAN DEFAULT false,
    start_time TIME DEFAULT '09:00',
    end_time TIME DEFAULT '18:00'
);
COMMENT ON TABLE work_schedules IS 'Шаблоны графиков работы';

-- Периоды KPI (например, квартал, год)
CREATE TABLE kpi_periods (
    period_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT kpi_period_dates CHECK (start_date <= end_date)
);
COMMENT ON TABLE kpi_periods IS 'Периоды оценки KPI';

-- Показатели KPI
CREATE TABLE kpi_indicators (
    indicator_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(50),          -- единица измерения (%, шт., руб.)
    target_value DECIMAL(10,2),-- плановое значение
    weight DECIMAL(5,2)        -- вес показателя в общей оценке (сумма весов = 100)
);
COMMENT ON TABLE kpi_indicators IS 'Показатели для оценки эффективности';

-- Кандидаты (для HR-модуля)
CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    position_applied INTEGER REFERENCES positions(position_id),
    status VARCHAR(30) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'interviewed', 'offered', 'hired', 'rejected')),
    source VARCHAR(100),        -- откуда узнал о вакансии
    resume_text TEXT,           -- текст резюме для полнотекстового поиска
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE candidates IS 'Кандидаты на вакансии';

-- ============================================
-- 2. Таблица сотрудников (ядро)
-- ============================================
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    personnel_number VARCHAR(20) UNIQUE,               -- табельный номер
    full_name VARCHAR(150) NOT NULL,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    hire_date DATE NOT NULL,
    termination_date DATE,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    position_id INTEGER NOT NULL REFERENCES positions(position_id),
    manager_id INTEGER REFERENCES employees(employee_id), -- непосредственный руководитель
    schedule_id INTEGER REFERENCES work_schedules(schedule_id), -- график работы
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT hire_termination_check CHECK (termination_date IS NULL OR termination_date >= hire_date)
);
COMMENT ON TABLE employees IS 'Основная информация о сотрудниках';
COMMENT ON COLUMN employees.personnel_number IS 'Табельный номер (уникальный)';
COMMENT ON COLUMN employees.manager_id IS 'Непосредственный руководитель (ссылка на другого сотрудника)';

-- ============================================
-- 3. Зависимые от сотрудников таблицы
-- ============================================

-- Адреса сотрудников (история)
CREATE TABLE employee_addresses (
    address_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    address_type VARCHAR(30) NOT NULL CHECK (address_type IN ('registration', 'residential', 'temporary')),
    country VARCHAR(100) DEFAULT 'Россия',
    region VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    street VARCHAR(200),
    house VARCHAR(20),
    apartment VARCHAR(20),
    postal_code VARCHAR(10),
    valid_from DATE NOT NULL,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT address_dates CHECK (valid_to IS NULL OR valid_to >= valid_from)
);
COMMENT ON TABLE employee_addresses IS 'Адреса сотрудников с историей';

-- Семейное положение и члены семьи
CREATE TABLE family_members (
    member_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    relationship VARCHAR(50) NOT NULL CHECK (relationship IN ('spouse', 'child', 'parent', 'other')),
    birth_date DATE,
    is_dependent BOOLEAN DEFAULT false,   -- находится на иждивении
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE family_members IS 'Члены семьи сотрудников';

-- Банковские реквизиты сотрудников
CREATE TABLE employee_bank_details (
    bank_detail_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    bank_name VARCHAR(200) NOT NULL,
    bik VARCHAR(9) NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    correspondent_account VARCHAR(20),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE employee_bank_details IS 'Банковские реквизиты для зарплаты';

-- ============================================
-- 4. Учёт рабочего времени (расширенный)
-- ============================================
CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    hours_worked NUMERIC(4,2) GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (check_out - check_in)) / 3600
    ) STORED,
    status VARCHAR(20) DEFAULT 'present' CHECK (status IN ('present', 'absent', 'vacation', 'sick', 'dayoff', 'remote')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (employee_id, work_date),
    CONSTRAINT check_times CHECK (check_out IS NULL OR check_out >= check_in)
);
COMMENT ON TABLE attendance IS 'Детальные отметки рабочего времени';

-- ============================================
-- 5. Отпуска и больничные
-- ============================================
CREATE TABLE leave_requests (
    request_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    leave_type VARCHAR(30) NOT NULL CHECK (leave_type IN ('vacation', 'sick', 'unpaid', 'maternity', 'other')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approved_by INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dates_check CHECK (start_date <= end_date)
);
COMMENT ON TABLE leave_requests IS 'Заявки на отпуска и отгулы';

-- ============================================
-- 6. Проекты и задачи
-- ============================================
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'on_hold', 'cancelled')),
    manager_id INTEGER,   -- внешний ключ добавим позже
    budget DECIMAL(12,2), -- плановый бюджет
    actual_cost DECIMAL(12,2), -- фактические затраты
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT project_dates CHECK (end_date IS NULL OR end_date >= start_date)
);
COMMENT ON TABLE projects IS 'Проекты компании';

CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    assigned_to INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL,
    deadline DATE,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    estimated_hours NUMERIC(6,2),  -- оценка трудозатрат
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'completed', 'blocked')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE tasks IS 'Задачи по проектам';

CREATE TABLE project_team (
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
    role VARCHAR(100),
    joined_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (project_id, employee_id)
);
COMMENT ON TABLE project_team IS 'Состав проектных команд';

-- ============================================
-- 7. Зарплата и финансы
-- ============================================
CREATE TABLE salaries (
    salary_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    effective_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE salaries IS 'История окладов сотрудников';

CREATE TABLE payroll (
    payroll_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    base_salary DECIMAL(10,2) NOT NULL,
    bonus DECIMAL(10,2) DEFAULT 0,
    deductions DECIMAL(10,2) DEFAULT 0,
    net_amount DECIMAL(10,2) GENERATED ALWAYS AS (base_salary + bonus - deductions) STORED,
    payment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT period_check CHECK (period_start <= period_end)
);
COMMENT ON TABLE payroll IS 'Расчётные листы по зарплате';

-- ============================================
-- 8. Оборудование (активы)
-- ============================================
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) UNIQUE,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    warranty_until DATE,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'assigned', 'repair', 'retired')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE assets IS 'Оборудование (компьютеры, телефоны и т.п.)';

CREATE TABLE asset_assignments (
    assignment_id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    returned_date DATE,
    condition_on_return VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT assignment_dates CHECK (returned_date IS NULL OR returned_date >= assigned_date)
);
COMMENT ON TABLE asset_assignments IS 'История закрепления оборудования за сотрудниками';

-- ============================================
-- 9. Обучение и сертификаты
-- ============================================
CREATE TABLE certificates (
    certificate_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    issue_date DATE NOT NULL,
    expiry_date DATE,
    grade VARCHAR(20),
    verification_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cert_dates CHECK (expiry_date IS NULL OR expiry_date >= issue_date)
);
COMMENT ON TABLE certificates IS 'Сертификаты, полученные сотрудниками';

-- ============================================
-- 10. Навыки сотрудников
-- ============================================
CREATE TABLE employee_skills (
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    level INTEGER CHECK (level BETWEEN 1 AND 5),  -- 1-начальный, 5-эксперт
    PRIMARY KEY (employee_id, skill_id)
);
COMMENT ON TABLE employee_skills IS 'Навыки, которыми владеют сотрудники';

-- ============================================
-- 11. Интервью с кандидатами
-- ============================================
CREATE TABLE interviews (
    interview_id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL, -- интервьюер
    interview_date TIMESTAMP NOT NULL,
    feedback TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 10),
    status VARCHAR(30) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE interviews IS 'Собеседования с кандидатами';

-- ============================================
-- 12. KPI сотрудников
-- ============================================
CREATE TABLE employee_kpi_results (
    result_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    period_id INTEGER NOT NULL REFERENCES kpi_periods(period_id),
    indicator_id INTEGER NOT NULL REFERENCES kpi_indicators(indicator_id),
    actual_value DECIMAL(10,2),
    score DECIMAL(5,2), -- итоговая оценка по показателю (может рассчитываться)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (employee_id, period_id, indicator_id)
);
COMMENT ON TABLE employee_kpi_results IS 'Результаты оценки KPI сотрудников';

-- ============================================
-- 13. Командировки
-- ============================================
CREATE TABLE business_trips (
    trip_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    destination VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    purpose TEXT,
    report TEXT,
    status VARCHAR(30) DEFAULT 'planned' CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT trip_dates CHECK (start_date <= end_date)
);
COMMENT ON TABLE business_trips IS 'Командировки сотрудников';

-- ============================================
-- 14. Документы (электронные образы)
-- ============================================
CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,  -- путь к файлу или ссылка
    mime_type VARCHAR(100),
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('passport', 'diploma', 'contract', 'certificate', 'other')),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE documents IS 'Хранилище документов (файлы)';

-- Связь документов с сотрудниками (многие-ко-многим)
CREATE TABLE employee_documents (
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (employee_id, document_id)
);
COMMENT ON TABLE employee_documents IS 'Привязка документов к сотрудникам';

-- ============================================
-- 15. Аудит изменений (упрощённый вариант)
-- ============================================
CREATE TABLE audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id INTEGER NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by INTEGER REFERENCES employees(employee_id), -- кто изменил (если известен)
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE audit_log IS 'Лог изменений данных (заполняется триггерами)';

-- ============================================
-- Примечание: внешние ключи для manager_id в departments и projects будут добавлены позже
-- ============================================