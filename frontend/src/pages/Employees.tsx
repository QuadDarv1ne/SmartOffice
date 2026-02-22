import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Spinner, Badge, FormControl, Row, Col } from 'react-bootstrap'
import { getEmployees, createEmployee, deleteEmployee, Employee, EmployeeCreate } from '../api/employees'
import { getDepartments, Department } from '../api/departments'

const Employees = () => {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [search, setSearch] = useState('')
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const limit = 10

  const [newEmployee, setNewEmployee] = useState<EmployeeCreate>({
    full_name: '',
    email: '',
    phone: '',
    hire_date: new Date().toISOString().split('T')[0],
    department_id: 1,
    position_id: 1,
  })

  useEffect(() => {
    fetchEmployees()
    fetchDepartments()
  }, [page, search])

  const fetchEmployees = async () => {
    setLoading(true)
    try {
      const data = await getEmployees({ skip: page * limit, limit, search: search || undefined })
      setEmployees(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchDepartments = async () => {
    try {
      const data = await getDepartments()
      setDepartments(data)
    } catch (error) {
      console.error('Failed to fetch departments:', error)
    }
  }

  const handleCreate = async () => {
    try {
      await createEmployee(newEmployee)
      setShowModal(false)
      fetchEmployees()
      setNewEmployee({
        full_name: '',
        email: '',
        phone: '',
        hire_date: new Date().toISOString().split('T')[0],
        department_id: 1,
        position_id: 1,
      })
    } catch (error) {
      console.error('Failed to create employee:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить сотрудника?')) {
      try {
        await deleteEmployee(id)
        fetchEmployees()
      } catch (error) {
        console.error('Failed to delete employee:', error)
      }
    }
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <div className="page-header d-flex justify-content-between align-items-center">
        <h1>Сотрудники</h1>
        <Button onClick={() => setShowModal(true)}>
          + Добавить сотрудника
        </Button>
      </div>

      <Row className="mb-3">
        <Col md={4}>
          <FormControl
            placeholder="Поиск по имени..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </Col>
      </Row>

      {loading ? (
        <div className="loading-spinner">
          <Spinner animation="border" />
        </div>
      ) : (
        <>
          <Table hover responsive>
            <thead>
              <tr>
                <th>ID</th>
                <th>ФИО</th>
                <th>Email</th>
                <th>Телефон</th>
                <th>Отдел</th>
                <th>Дата найма</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.employee_id}>
                  <td>{emp.employee_id}</td>
                  <td>{emp.full_name}</td>
                  <td>{emp.email || '-'}</td>
                  <td>{emp.phone || '-'}</td>
                  <td>{departments.find(d => d.department_id === emp.department_id)?.name || '-'}</td>
                  <td>{emp.hire_date}</td>
                  <td>
                    <Badge bg={emp.termination_date ? 'secondary' : 'success'}>
                      {emp.termination_date ? 'Уволен' : 'Работает'}
                    </Badge>
                  </td>
                  <td>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleDelete(emp.employee_id)}
                    >
                      Удалить
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="d-flex justify-content-between align-items-center">
            <span>Всего: {total}</span>
            <div className="d-flex gap-2">
              <Button
                variant="outline-primary"
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
              >
                Назад
              </Button>
              <span className="py-2">
                {page + 1} / {totalPages || 1}
              </span>
              <Button
                variant="outline-primary"
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
              >
                Вперёд
              </Button>
            </div>
          </div>
        </>
      )}

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Новый сотрудник</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>ФИО</Form.Label>
              <Form.Control
                value={newEmployee.full_name}
                onChange={(e) => setNewEmployee({ ...newEmployee, full_name: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={newEmployee.email}
                onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Телефон</Form.Label>
              <Form.Control
                value={newEmployee.phone}
                onChange={(e) => setNewEmployee({ ...newEmployee, phone: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Дата найма</Form.Label>
              <Form.Control
                type="date"
                value={newEmployee.hire_date}
                onChange={(e) => setNewEmployee({ ...newEmployee, hire_date: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Отдел</Form.Label>
              <Form.Select
                value={newEmployee.department_id}
                onChange={(e) => setNewEmployee({ ...newEmployee, department_id: Number(e.target.value) })}
              >
                {departments.map((dept) => (
                  <option key={dept.department_id} value={dept.department_id}>
                    {dept.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Отмена
          </Button>
          <Button variant="primary" onClick={handleCreate}>
            Создать
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  )
}

export default Employees
