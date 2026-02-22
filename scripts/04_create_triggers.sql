-- ============================================
-- Файл: 04_create_triggers.sql
-- Назначение: создание триггеров для поддержки целостности и аудита
-- ============================================

-- 1. Триггер для обновления updated_at в employees
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 2. Триггер для аудита изменений в таблице employees (пример)
CREATE OR REPLACE FUNCTION audit_employees()
RETURNS TRIGGER AS $$
DECLARE
    old_json JSONB;
    new_json JSONB;
    operation TEXT;
    record_id INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        operation := 'INSERT';
        new_json := to_jsonb(NEW);
        record_id := NEW.employee_id;
    ELSIF TG_OP = 'UPDATE' THEN
        operation := 'UPDATE';
        old_json := to_jsonb(OLD);
        new_json := to_jsonb(NEW);
        record_id := NEW.employee_id;
    ELSIF TG_OP = 'DELETE' THEN
        operation := 'DELETE';
        old_json := to_jsonb(OLD);
        record_id := OLD.employee_id;
    END IF;

    INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
    VALUES ('employees', operation, record_id, old_json, new_json, NULL); -- changed_by можно передавать из контекста

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Включаем аудит для employees (опционально, может замедлить работу)
-- DROP TRIGGER IF EXISTS audit_employees_trigger ON employees;
-- CREATE TRIGGER audit_employees_trigger
--     AFTER INSERT OR UPDATE OR DELETE ON employees
--     FOR EACH ROW EXECUTE FUNCTION audit_employees();

-- 3. Триггер для проверки возможности увольнения сотрудника
CREATE OR REPLACE FUNCTION check_termination()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.termination_date IS NOT NULL THEN
        -- Проверяем, есть ли незавершённые задачи
        IF EXISTS (SELECT 1 FROM tasks WHERE assigned_to = NEW.employee_id AND status NOT IN ('completed', 'blocked')) THEN
            RAISE EXCEPTION 'Нельзя уволить сотрудника: у него есть незавершённые задачи';
        END IF;
        -- Проверяем, есть ли выданное и не возвращённое оборудование
        IF EXISTS (SELECT 1 FROM asset_assignments WHERE employee_id = NEW.employee_id AND returned_date IS NULL) THEN
            RAISE EXCEPTION 'Нельзя уволить сотрудника: за ним числится оборудование';
        END IF;
        -- Проверяем, есть ли будущие отпуска
        IF EXISTS (SELECT 1 FROM leave_requests WHERE employee_id = NEW.employee_id AND start_date > CURRENT_DATE AND status = 'approved') THEN
            RAISE EXCEPTION 'Нельзя уволить сотрудника: у него есть одобренные будущие отпуска';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_termination_trigger
    BEFORE UPDATE OF termination_date ON employees
    FOR EACH ROW
    EXECUTE FUNCTION check_termination();

-- 4. Триггер для автоматического создания табельного номера при добавлении сотрудника
CREATE OR REPLACE FUNCTION generate_personnel_number()
RETURNS TRIGGER AS $$
DECLARE
    next_number INTEGER;
BEGIN
    IF NEW.personnel_number IS NULL THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(personnel_number FROM 3) AS INTEGER)), 0) + 1
        INTO next_number
        FROM employees
        WHERE personnel_number LIKE 'SN-%';
        NEW.personnel_number := 'SN-' || LPAD(next_number::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_personnel_number_trigger
    BEFORE INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION generate_personnel_number();

-- 5. Триггер для обновления updated_at в employee_bank_details
CREATE TRIGGER update_bank_details_updated_at
    BEFORE UPDATE ON employee_bank_details
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Триггер для проверки пересечения отпусков (дублирует исключающее ограничение, можно оставить для информативности)
-- Но ограничение EXCLUDE уже работает.

-- 7. Триггер для автоматического расчёта hours_worked в attendance (если не использовать GENERATED)
-- Но мы использовали GENERATED, поэтому не нужен.