import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Spinner, Badge, FormControl, Row, Col, FormSelect } from 'react-bootstrap'
import { getProjects, createProject, deleteProject, Project, ProjectCreate } from '../api/projects'

const Projects = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const limit = 10

  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: '',
    description: '',
    start_date: new Date().toISOString().split('T')[0],
    status: 'active',
  })

  useEffect(() => {
    fetchProjects()
  }, [page, statusFilter])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const data = await getProjects({ skip: page * limit, limit, status: statusFilter || undefined })
      setProjects(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await createProject(newProject)
      setShowModal(false)
      fetchProjects()
      setNewProject({
        name: '',
        description: '',
        start_date: new Date().toISOString().split('T')[0],
        status: 'active',
      })
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить проект?')) {
      try {
        await deleteProject(id)
        fetchProjects()
      } catch (error) {
        console.error('Failed to delete project:', error)
      }
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'success',
      completed: 'primary',
      paused: 'warning',
      cancelled: 'danger',
    }
    const labels: Record<string, string> = {
      active: 'Активный',
      completed: 'Завершён',
      paused: 'Приостановлен',
      cancelled: 'Отменён',
    }
    return <Badge bg={colors[status] || 'secondary'}>{labels[status] || status}</Badge>
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <div className="page-header d-flex justify-content-between align-items-center">
        <h1>Проекты</h1>
        <Button onClick={() => setShowModal(true)}>
          + Новый проект
        </Button>
      </div>

      <Row className="mb-3">
        <Col md={3}>
          <FormSelect
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="active">Активные</option>
            <option value="completed">Завершённые</option>
            <option value="paused">Приостановленные</option>
            <option value="cancelled">Отменённые</option>
          </FormSelect>
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
                <th>Название</th>
                <th>Описание</th>
                <th>Дата начала</th>
                <th>Статус</th>
                <th>Бюджет</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((proj) => (
                <tr key={proj.project_id}>
                  <td>{proj.project_id}</td>
                  <td>{proj.name}</td>
                  <td>{proj.description?.substring(0, 50) || '-'}{proj.description && proj.description.length > 50 ? '...' : ''}</td>
                  <td>{proj.start_date || '-'}</td>
                  <td>{getStatusBadge(proj.status)}</td>
                  <td>{proj.budget ? `${proj.budget} ₽` : '-'}</td>
                  <td>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleDelete(proj.project_id)}
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
              <span className="py-2">{page + 1} / {totalPages || 1}</span>
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
          <Modal.Title>Новый проект</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Название</Form.Label>
              <Form.Control
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Описание</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Дата начала</Form.Label>
              <Form.Control
                type="date"
                value={newProject.start_date}
                onChange={(e) => setNewProject({ ...newProject, start_date: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Статус</Form.Label>
              <Form.Select
                value={newProject.status}
                onChange={(e) => setNewProject({ ...newProject, status: e.target.value })}
              >
                <option value="active">Активный</option>
                <option value="paused">Приостановлен</option>
                <option value="completed">Завершён</option>
                <option value="cancelled">Отменён</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Бюджет</Form.Label>
              <Form.Control
                type="number"
                value={newProject.budget || ''}
                onChange={(e) => setNewProject({ ...newProject, budget: Number(e.target.value) })}
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

export default Projects
