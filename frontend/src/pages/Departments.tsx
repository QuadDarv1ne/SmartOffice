import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Spinner, Badge } from 'react-bootstrap'
import { getDepartments, createDepartment, deleteDepartment, Department, DepartmentCreate } from '../api/departments'

const Departments = () => {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [newDepartment, setNewDepartment] = useState<DepartmentCreate>({ name: '' })

  useEffect(() => {
    fetchDepartments()
  }, [])

  const fetchDepartments = async () => {
    setLoading(true)
    try {
      const data = await getDepartments()
      setDepartments(data)
    } catch (error) {
      console.error('Failed to fetch departments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await createDepartment(newDepartment)
      setShowModal(false)
      fetchDepartments()
      setNewDepartment({ name: '' })
    } catch (error) {
      console.error('Failed to create department:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить отдел?')) {
      try {
        await deleteDepartment(id)
        fetchDepartments()
      } catch (error) {
        console.error('Failed to delete department:', error)
      }
    }
  }

  return (
    <div>
      <div className="page-header d-flex justify-content-between align-items-center">
        <h1>Отделы</h1>
        <Button onClick={() => setShowModal(true)}>
          + Добавить отдел
        </Button>
      </div>

      {loading ? (
        <div className="loading-spinner">
          <Spinner animation="border" />
        </div>
      ) : (
        <Table hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Руководитель</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept) => (
              <tr key={dept.department_id}>
                <td>{dept.department_id}</td>
                <td>{dept.name}</td>
                <td>{dept.manager_id || '-'}</td>
                <td>
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleDelete(dept.department_id)}
                  >
                    Удалить
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Новый отдел</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Название</Form.Label>
              <Form.Control
                value={newDepartment.name}
                onChange={(e) => setNewDepartment({ name: e.target.value })}
              />
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

export default Departments
