-- ============================================
-- Файл: 03_create_indexes.sql
-- Назначение: создание дополнительных индексов
-- ============================================

-- Индексы для employees
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_position ON employees(position_id);
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_full_name ON employees(full_name);
CREATE INDEX idx_employees_personnel_number ON employees(personnel_number);
-- Полнотекстовый поиск по ФИО (используем GIN с триграммами)
CREATE INDEX idx_employees_full_name_trgm ON employees USING gin (full_name gin_trgm_ops);

-- Индексы для employee_addresses
CREATE INDEX idx_employee_addresses_employee ON employee_addresses(employee_id);

-- Индексы для family_members
CREATE INDEX idx_family_members_employee ON family_members(employee_id);

-- Индексы для employee_bank_details
CREATE INDEX idx_employee_bank_details_employee ON employee_bank_details(employee_id);

-- Индексы для attendance
CREATE INDEX idx_attendance_employee_date ON attendance(employee_id, work_date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- Индексы для leave_requests
CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_dates ON leave_requests(start_date, end_date);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);

-- Индексы для projects
CREATE INDEX idx_projects_manager ON projects(manager_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_name_trgm ON projects USING gin (name gin_trgm_ops);

-- Индексы для tasks
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_title_trgm ON tasks USING gin (title gin_trgm_ops);

-- Индексы для project_team
CREATE INDEX idx_project_team_employee ON project_team(employee_id);

-- Индексы для salaries
CREATE INDEX idx_salaries_employee ON salaries(employee_id);
CREATE INDEX idx_salaries_date ON salaries(effective_date);

-- Индексы для payroll
CREATE INDEX idx_payroll_employee ON payroll(employee_id);
CREATE INDEX idx_payroll_period ON payroll(period_start, period_end);

-- Индексы для assets
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_supplier ON assets(supplier_id);
CREATE INDEX idx_assets_serial_number ON assets(serial_number);

-- Индексы для asset_assignments
CREATE INDEX idx_asset_assignments_asset ON asset_assignments(asset_id);
CREATE INDEX idx_asset_assignments_employee ON asset_assignments(employee_id);

-- Индексы для certificates
CREATE INDEX idx_certificates_employee ON certificates(employee_id);
CREATE INDEX idx_certificates_expiry ON certificates(expiry_date);

-- Индексы для employee_skills
CREATE INDEX idx_employee_skills_skill ON employee_skills(skill_id);

-- Индексы для candidates
CREATE INDEX idx_candidates_position ON candidates(position_applied);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_full_name_trgm ON candidates USING gin (full_name gin_trgm_ops);
CREATE INDEX idx_candidates_resume_text ON candidates USING gin (to_tsvector('russian', resume_text));

-- Индексы для interviews
CREATE INDEX idx_interviews_candidate ON interviews(candidate_id);
CREATE INDEX idx_interviews_employee ON interviews(employee_id);
CREATE INDEX idx_interviews_date ON interviews(interview_date);

-- Индексы для employee_kpi_results
CREATE INDEX idx_employee_kpi_results_employee ON employee_kpi_results(employee_id);
CREATE INDEX idx_employee_kpi_results_period ON employee_kpi_results(period_id);

-- Индексы для business_trips
CREATE INDEX idx_business_trips_employee ON business_trips(employee_id);
CREATE INDEX idx_business_trips_dates ON business_trips(start_date, end_date);

-- Индексы для documents
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_employee_documents_employee ON employee_documents(employee_id);

-- Индексы для audit_log
CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);