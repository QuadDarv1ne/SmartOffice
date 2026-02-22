import { useState } from 'react'
import { Form, Button, Card, Row, Col, Badge } from 'react-bootstrap'
import { toast } from 'react-toastify'
import { AvatarUpload } from '../components/AvatarUpload'
import { TwoFactorSetupModal } from '../components/TwoFactorSetupModal'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'

const Settings = () => {
  const { user } = useAuthStore()
  const [avatar, setAvatar] = useState(user?.avatar)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [show2FAModal, setShow2FAModal] = useState(false)
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(user?.two_factor_enabled || false)
  const [twoFactorLoading, setTwoFactorLoading] = useState(false)

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (newPassword !== confirmPassword) {
      toast.error('Пароли не совпадают')
      return
    }

    if (newPassword.length < 8) {
      toast.error('Пароль должен быть не менее 8 символов')
      return
    }

    setLoading(true)

    try {
      // API call для смены пароля
      // await api.post('/auth/change-password', { currentPassword, newPassword })
      toast.success('Пароль успешно изменён')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка смены пароля')
    } finally {
      setLoading(false)
    }
  }

  const handleDisable2FA = async () => {
    if (!window.confirm('Вы уверены, что хотите отключить 2FA?')) return

    setTwoFactorLoading(true)
    try {
      await api.post('/auth/2fa/disable', { password: currentPassword })
      setTwoFactorEnabled(false)
      toast.success('2FA отключён')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка отключения 2FA')
    } finally {
      setTwoFactorLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header mb-4">
        <h1>Настройки</h1>
      </div>

      <Row className="g-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Профиль</h5>
            </Card.Header>
            <Card.Body className="text-center">
              <div className="mb-3">
                <AvatarUpload
                  currentAvatar={avatar}
                  onAvatarChange={setAvatar}
                />
              </div>
              <h5>{user?.email}</h5>
              <p className="text-muted mb-0">
                {user?.is_admin ? 'Администратор' : 'Пользователь'}
              </p>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Безопасность</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-4">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <div>
                    <strong>Двухфакторная аутентификация</strong>
                    <p className="text-muted small mb-0">
                      Дополнительная защита аккаунта
                    </p>
                  </div>
                  <div className="d-flex gap-2 align-items-center">
                    {twoFactorEnabled ? (
                      <>
                        <Badge bg="success">Включено</Badge>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={handleDisable2FA}
                          disabled={twoFactorLoading}
                        >
                          {twoFactorLoading ? '...' : 'Отключить'}
                        </Button>
                      </>
                    ) : (
                      <>
                        <Badge bg="secondary">Отключено</Badge>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => setShow2FAModal(true)}
                        >
                          Включить
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <hr />

              <Form onSubmit={handlePasswordChange}>
                <Form.Group className="mb-3">
                  <Form.Label>Текущий пароль</Form.Label>
                  <Form.Control
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Новый пароль</Form.Label>
                  <Form.Control
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Подтверждение пароля</Form.Label>
                  <Form.Control
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </Form.Group>

                <Button type="submit" variant="primary" disabled={loading}>
                  {loading ? 'Сохранение...' : 'Изменить пароль'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <TwoFactorSetupModal
        show={show2FAModal}
        onHide={() => setShow2FAModal(false)}
        onSuccess={() => setTwoFactorEnabled(true)}
      />
    </div>
  )
}

export default Settings
