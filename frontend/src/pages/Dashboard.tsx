import { useEffect, useState } from 'react'
import { Row, Col, Card, Spinner } from 'react-bootstrap'
import { getDashboardStats, DashboardStats } from '../api/dashboard'

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="loading-spinner">
        <Spinner animation="border" />
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Дашборд</h1>
      </div>

      <Row className="g-4 mb-4">
        <Col md={3}>
          <div className="stat-card employees">
            <h3>{stats?.employees.active || 0}</h3>
            <p>Активных сотрудников</p>
          </div>
        </Col>
        <Col md={3}>
          <div className="stat-card projects">
            <h3>{stats?.projects.active || 0}</h3>
            <p>Активных проектов</p>
          </div>
        </Col>
        <Col md={3}>
          <div className="stat-card tasks">
            <h3>{stats?.tasks.pending || 0}</h3>
            <p>Задач в работе</p>
          </div>
        </Col>
        <Col md={3}>
          <div className="stat-card assets">
            <h3>{stats?.assets.total || 0}</h3>
            <p>Единиц оборудования</p>
          </div>
        </Col>
      </Row>

      <Row className="g-4">
        <Col md={6}>
          <Card className="h-100">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Сводка</h5>
            </Card.Header>
            <Card.Body>
              <table className="table table-borderless">
                <tbody>
                  <tr>
                    <td>Всего сотрудников</td>
                    <td className="text-end fw-bold">{stats?.employees.total || 0}</td>
                  </tr>
                  <tr>
                    <td>Всего проектов</td>
                    <td className="text-end fw-bold">{stats?.projects.total || 0}</td>
                  </tr>
                  <tr>
                    <td>Всего задач</td>
                    <td className="text-end fw-bold">{stats?.tasks.total || 0}</td>
                  </tr>
                  <tr>
                    <td>Завершённых задач</td>
                    <td className="text-end fw-bold text-success">{stats?.tasks.completed || 0}</td>
                  </tr>
                  <tr>
                    <td>Отделов</td>
                    <td className="text-end fw-bold">{stats?.departments || 0}</td>
                  </tr>
                  <tr>
                    <td>Оборудования в использовании</td>
                    <td className="text-end fw-bold">{stats?.assets.in_use || 0}</td>
                  </tr>
                </tbody>
              </table>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="h-100">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Статус задач</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-flex flex-column gap-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span>Новые</span>
                  <span className="badge bg-secondary">{stats?.tasks.pending || 0}</span>
                </div>
                <div className="d-flex justify-content-between align-items-center">
                  <span>В работе</span>
                  <span className="badge bg-primary">{stats?.tasks.pending || 0}</span>
                </div>
                <div className="d-flex justify-content-between align-items-center">
                  <span>Завершены</span>
                  <span className="badge bg-success">{stats?.tasks.completed || 0}</span>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
