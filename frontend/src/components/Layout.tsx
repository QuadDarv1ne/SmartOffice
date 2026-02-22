import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Nav, Navbar, Container, Dropdown } from 'react-bootstrap'
import { logout } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { toast } from 'react-toastify'
import { NotificationsBell } from './NotificationsBell'
import { ThemeToggle } from './ThemeToggle'

interface LayoutProps {
  onLogout: () => void
}

const Layout = ({ onLogout }: LayoutProps) => {
  const { user, logout: logoutStore } = useAuthStore()
  const navigate = useNavigate()
  const userEmail = user?.email || localStorage.getItem('userEmail') || 'user@example.com'

  const handleLogout = async () => {
    await logout()
    logoutStore()
    toast.success('Выход выполнен')
    navigate('/login')
    onLogout()
  }

  return (
    <div className="d-flex">
      {/* Sidebar */}
      <div className="sidebar d-flex flex-column" style={{ width: '250px' }}>
        <div className="p-3 text-white border-bottom border-secondary">
          <h4 className="mb-0">
            <i className="bi bi-building me-2"></i>
            SmartOffice
          </h4>
        </div>
        <Nav className="flex-column flex-grow-1 pt-2">
          <Nav.Link as={NavLink} to="/dashboard">
            <i className="bi bi-speedometer2"></i>
            Дашборд
          </Nav.Link>
          <Nav.Link as={NavLink} to="/employees">
            <i className="bi bi-people"></i>
            Сотрудники
          </Nav.Link>
          <Nav.Link as={NavLink} to="/departments">
            <i className="bi bi-diagram-3"></i>
            Отделы
          </Nav.Link>
          <Nav.Link as={NavLink} to="/projects">
            <i className="bi bi-kanban"></i>
            Проекты
          </Nav.Link>
          <Nav.Link as={NavLink} to="/tasks">
            <i className="bi bi-list-check"></i>
            Задачи
          </Nav.Link>
          <Nav.Link as={NavLink} to="/assets">
            <i className="bi bi-pc-display"></i>
            Оборудование
          </Nav.Link>
        </Nav>
        <div className="p-3 text-white-50 small">
          © 2025 SmartOffice
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow-1 bg-light">
        {/* Top navbar */}
        <Navbar bg="white" className="shadow-sm px-4">
          <Container fluid>
            <Navbar.Brand className="fw-semibold text-dark">
              Система управления
            </Navbar.Brand>
            <Navbar.Collapse className="justify-content-end">
              <div className="d-flex align-items-center gap-3">
                <ThemeToggle />
                <NotificationsBell />
                <Dropdown align="end">
                  <Dropdown.Toggle variant="light" id="user-dropdown">
                    <span className="avatar me-2">
                      {userEmail.charAt(0).toUpperCase()}
                    </span>
                    {userEmail}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item href="#profile">Профиль</Dropdown.Item>
                    <Dropdown.Item href="/settings">Настройки</Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={handleLogout}>
                      <i className="bi bi-box-arrow-right me-2"></i>
                      Выйти
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {/* Page content */}
        <div className="main-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default Layout
