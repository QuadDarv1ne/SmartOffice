-- ============================================
-- Файл: 06_views.sql (опционально)
-- Назначение: создание полезных представлений
-- ============================================

-- 1. Информация о сотрудниках с отделами и должностями
CREATE VIEW v_employee_info AS
SELECT
    e.employee_id,
    e.personnel_number,
    e.full_name,
    e.birth_date,
    e.email,
    e.phone,
    e.hire_date,
    e.termination_date,
    d.name AS department,
    p.title AS position,
    CONCAT(m.full_name, ' (', m.personnel_number, ')') AS manager_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN positions p ON e.position_id = p.position_id
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- 2. Текущие оклады сотрудников
CREATE VIEW v_current_salaries AS
SELECT DISTINCT ON (e.employee_id)
    e.employee_id,
    e.full_name,
    s.amount AS current_salary,
    s.effective_date
FROM employees e
LEFT JOIN salaries s ON e.employee_id = s.employee_id
ORDER BY e.employee_id, s.effective_date DESC;

-- 3. Загруженность сотрудников (количество активных задач)
CREATE VIEW v_employee_task_load AS
SELECT
    e.employee_id,
    e.full_name,
    COUNT(t.task_id) AS active_tasks
FROM employees e
LEFT JOIN tasks t ON e.employee_id = t.assigned_to AND t.status IN ('new', 'in_progress')
GROUP BY e.employee_id, e.full_name;

-- 4. Отпуска на текущий месяц
CREATE VIEW v_current_leave AS
SELECT
    e.full_name,
    lr.start_date,
    lr.end_date,
    lr.leave_type,
    lr.status
FROM leave_requests lr
JOIN employees e ON lr.employee_id = e.employee_id
WHERE lr.start_date <= (CURRENT_DATE + INTERVAL '1 month') AND lr.end_date >= CURRENT_DATE;

-- 5. Оборудование за сотрудниками
CREATE VIEW v_asset_assignments AS
SELECT
    a.name AS asset_name,
    a.type,
    a.serial_number,
    e.full_name AS assigned_to,
    aa.assigned_date,
    aa.returned_date
FROM asset_assignments aa
JOIN assets a ON aa.asset_id = a.asset_id
JOIN employees e ON aa.employee_id = e.employee_id
WHERE aa.returned_date IS NULL;

-- 6. Итоги KPI по сотрудникам за последний период
CREATE VIEW v_kpi_summary AS
SELECT
    e.full_name,
    kp.name AS period,
    ki.name AS indicator,
    kr.actual_value,
    ki.target_value,
    kr.score
FROM employee_kpi_results kr
JOIN employees e ON kr.employee_id = e.employee_id
JOIN kpi_periods kp ON kr.period_id = kp.period_id
JOIN kpi_indicators ki ON kr.indicator_id = ki.indicator_id
WHERE kp.is_active = true;

-- Материализованное представление для отчёта по зарплате (обновлять раз в месяц)
-- CREATE MATERIALIZED VIEW mv_payroll_report AS
-- SELECT ... ;