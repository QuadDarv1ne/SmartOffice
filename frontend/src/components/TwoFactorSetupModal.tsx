import { useState } from 'react'
import { Modal, Button, Form, Alert, Card } from 'react-bootstrap'
import { toast } from 'react-toastify'
import api from '../api/client'

interface TwoFactorSetupModalProps {
  show: boolean
  onHide: () => void
  onSuccess: () => void
}

export const TwoFactorSetupModal = ({ show, onHide, onSuccess }: TwoFactorSetupModalProps) => {
  const [step, setStep] = useState<'setup' | 'confirm'>('setup')
  const [loading, setLoading] = useState(false)
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [confirmCode, setConfirmCode] = useState('')

  const handleSetup = async () => {
    setLoading(true)
    try {
      const response = await api.post('/auth/2fa/setup')
      setQrCode(response.data.qr_code)
      setSecret(response.data.manual_entry_key)
      setBackupCodes(response.data.backup_codes)
      setStep('confirm')
      toast.info('Отсканируйте QR код в приложении аутентификации')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка настройки 2FA')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await api.post('/auth/2fa/confirm', { token: confirmCode })
      toast.success('2FA успешно включён!')
      onSuccess()
      onHide()
      setStep('setup')
      setConfirmCode('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Неверный код')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadBackupCodes = () => {
    const content = `SmartOffice Backup Codes\n========================\n\nСохраните эти коды в безопасном месте. Каждый код можно использовать только один раз.\n\n${backupCodes.join('\n')}`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'smartoffice-backup-codes.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Настройка двухфакторной аутентификации</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {step === 'setup' ? (
          <div>
            <Alert variant="info">
              <strong>Шаг 1:</strong> Отсканируйте QR код в приложении аутентификации
              (Google Authenticator, Authy, Microsoft Authenticator)
            </Alert>

            {qrCode && (
              <div className="text-center mb-4">
                <img src={qrCode} alt="QR Code" style={{ maxWidth: '250px' }} />
              </div>
            )}

            <Card className="mb-4">
              <Card.Header>Ручной ввод ключа</Card.Header>
              <Card.Body>
                <Form.Group>
                  <Form.Label>Ключ для ручного ввода:</Form.Label>
                  <Form.Control
                    type="text"
                    value={secret}
                    readOnly
                    className="font-monospace"
                  />
                </Form.Group>
              </Card.Body>
            </Card>

            <Button
              variant="primary"
              className="w-100"
              onClick={handleSetup}
              disabled={loading}
            >
              {loading ? 'Загрузка...' : 'Я отсканировал QR код'}
            </Button>
          </div>
        ) : (
          <div>
            <Alert variant="success">
              <strong>Шаг 2:</strong> Введите код из приложения для подтверждения
            </Alert>

            <Form.Group className="mb-4">
              <Form.Label>Код из приложения</Form.Label>
              <Form.Control
                type="text"
                value={confirmCode}
                onChange={(e) => setConfirmCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="text-center fs-4"
              />
            </Form.Group>

            <Card className="mb-4 bg-light">
              <Card.Body>
                <strong>⚠️ Backup коды</strong>
                <p className="mb-2 small text-muted">
                  Сохраните эти коды в безопасном месте. Они понадобятся для восстановления доступа.
                </p>
                <div className="d-grid gap-2">
                  <Button variant="outline-secondary" size="sm" onClick={handleDownloadBackupCodes}>
                    📥 Скачать backup коды
                  </Button>
                </div>
                <div className="mt-2 p-2 bg-white rounded border font-monospace small" style={{ maxHeight: '150px', overflowY: 'auto' }}>
                  {backupCodes.map((code, i) => (
                    <div key={i}>{code}</div>
                  ))}
                </div>
              </Card.Body>
            </Card>

            <div className="d-flex gap-2">
              <Button
                variant="secondary"
                className="flex-grow-1"
                onClick={() => setStep('setup')}
              >
                Назад
              </Button>
              <Button
                variant="primary"
                className="flex-grow-1"
                onClick={handleConfirm}
                disabled={!confirmCode || loading}
              >
                {loading ? 'Проверка...' : 'Подтвердить'}
              </Button>
            </div>
          </div>
        )}
      </Modal.Body>
    </Modal>
  )
}
