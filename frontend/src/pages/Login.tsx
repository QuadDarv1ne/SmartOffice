import { useState } from 'react'
import { Form, Button, Card, Alert } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { toast } from 'react-toastify'

interface LoginProps {
  onLogin: () => void
}

const Login = ({ onLogin }: LoginProps) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const loginStore = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await login({ email, password })
      loginStore.login(response.access_token, response.refresh_token, email)
      toast.success('Вход выполнен успешно!')
      onLogin()
      navigate('/dashboard')
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Ошибка авторизации'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <Card style={{ width: '400px' }} className="shadow">
        <Card.Body className="p-4">
          <div className="text-center mb-4">
            <h2 className="fw-bold text-primary">SmartOffice</h2>
            <p className="text-muted">Войдите в систему</p>
          </div>

          {error && <Alert variant="danger">{error}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                required
              />
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>Пароль</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </Form.Group>

            <Button
              type="submit"
              className="w-100"
              disabled={loading}
            >
              {loading ? 'Вход...' : 'Войти'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  )
}

export default Login
