import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Spinner, Badge, FormSelect, Row, Col } from 'react-bootstrap'
import { getTasks, createTask, deleteTask, Task, TaskCreate } from '../api/tasks'
import { getProjects, Project } from '../api/projects'
import { getEmployees, Employee } from '../api/employees'

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const limit = 10

  const [newTask, setNewTask] = useState<TaskCreate>({
    project_id: 1,
    title: '',
    description: '',
    priority: 'medium',
    status: 'new',
  })

  useEffect(() => {
    fetchTasks()
    fetchProjects()
    fetchEmployees()
  }, [page, statusFilter])

  const fetchTasks = async () => {
    setLoading(true)
    try {
      const data = await getTasks({ skip: page * limit, limit, status: statusFilter || undefined })
      setTasks(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchProjects = async () => {
    try {
      const data = await getProjects({ limit: 100 })
      setProjects(data.items)
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    }
  }

  const fetchEmployees = async () => {
    try {
      const data = await getEmployees({ limit: 100 })
      setEmployees(data.items)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    }
  }

  const handleCreate = async () => {
    try {
      await createTask(newTask)
      setShowModal(false)
      fetchTasks()
      setNewTask({
        project_id: 1,
        title: '',
        description: '',
        priority: 'medium',
        status: 'new',
      })
    } catch (error) {
      console.error('Failed to create task:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить задачу?')) {
      try {
        await deleteTask(id)
        fetchTasks()
      } catch (error) {
        console.error('Failed to delete task:', error)
      }
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: 'secondary',
      in_progress: 'primary',
      completed: 'success',
      cancelled: 'danger',
    }
    const labels: Record<string, string> = {
      new: 'Новая',
      in_progress: 'В работе',
      completed: 'Завершена',
      cancelled: 'Отменена',
    }
    return <Badge bg={colors[status] || 'secondary'}>{labels[status] || status}</Badge>
  }

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'success',
      medium: 'warning',
      high: 'danger',
    }
    const labels: Record<string, string> = {
      low: 'Низкий',
      medium: 'Средний',
      high: 'Высокий',
    }
    return <Badge bg={colors[priority] || 'secondary'}>{labels[priority] || priority}</Badge>
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <div className="page-header d-flex justify-content-between align-items-center">
        <h1>Задачи</h1>
        <Button onClick={() => setShowModal(true)}>
          + Новая задача
        </Button>
      </div>

      <Row className="mb-3">
        <Col md={3}>
          <FormSelect
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="new">Новые</option>
            <option value="in_progress">В работе</option>
            <option value="completed">Завершённые</option>
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
                <th>Проект</th>
                <th>Исполнитель</th>
                <th>Приоритет</th>
                <th>Статус</th>
                <th>Дедлайн</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.task_id}>
                  <td>{task.task_id}</td>
                  <td>{task.title}</td>
                  <td>{projects.find(p => p.project_id === task.project_id)?.name || '-'}</td>
                  <td>{employees.find(e => e.employee_id === task.assigned_to)?.full_name || '-'}</td>
                  <td>{getPriorityBadge(task.priority)}</td>
                  <td>{getStatusBadge(task.status)}</td>
                  <td>{task.deadline || '-'}</td>
                  <td>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleDelete(task.task_id)}
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
          <Modal.Title>Новая задача</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Название</Form.Label>
              <Form.Control
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Описание</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Проект</Form.Label>
              <Form.Select
                value={newTask.project_id}
                onChange={(e) => setNewTask({ ...newTask, project_id: Number(e.target.value) })}
              >
                {projects.map((proj) => (
                  <option key={proj.project_id} value={proj.project_id}>
                    {proj.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Исполнитель</Form.Label>
              <Form.Select
                value={newTask.assigned_to || ''}
                onChange={(e) => setNewTask({ ...newTask, assigned_to: Number(e.target.value) || undefined })}
              >
                <option value="">Не назначен</option>
                {employees.map((emp) => (
                  <option key={emp.employee_id} value={emp.employee_id}>
                    {emp.full_name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Приоритет</Form.Label>
              <Form.Select
                value={newTask.priority}
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
              >
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Дедлайн</Form.Label>
              <Form.Control
                type="date"
                value={newTask.deadline || ''}
                onChange={(e) => setNewTask({ ...newTask, deadline: e.target.value })}
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

export default Tasks
