-- ============================================
-- Файл: 02_add_constraints.sql
-- Назначение: добавление ограничений, требующих существования таблиц
-- ============================================

-- Внешние ключи для руководителей
ALTER TABLE departments
    ADD CONSTRAINT fk_departments_manager
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL;

ALTER TABLE projects
    ADD CONSTRAINT fk_projects_manager
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL;

-- Уникальность табельного номера (уже есть, но продублируем для надёжности)
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_personnel_number ON employees(personnel_number);

-- Ограничение: один активный основной банковский счёт на сотрудника
CREATE UNIQUE INDEX idx_employee_bank_details_default ON employee_bank_details (employee_id) WHERE is_default = true;

-- Ограничение: непересекающиеся отпуска для одного сотрудника (используем исключающее ограничение)
-- Требует расширения btree_gist
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE leave_requests
    ADD CONSTRAINT no_overlapping_leave
    EXCLUDE USING gist (
        employee_id WITH =,
        daterange(start_date, end_date, '[]') WITH &&
    ) WHERE (status IN ('approved', 'pending'));  -- только для активных заявок

-- Аналогично для командировок
ALTER TABLE business_trips
    ADD CONSTRAINT no_overlapping_trips
    EXCLUDE USING gist (
        employee_id WITH =,
        daterange(start_date, end_date, '[]') WITH &&
    ) WHERE (status IN ('planned', 'in_progress'));

-- Проверка, что дата увольнения не раньше дат в связанных записях (можно через триггеры)
-- Например, нельзя уволить сотрудника, если у него есть незавершённые задачи или выданное оборудование.
-- Это лучше реализовать на уровне приложения или через триггеры.