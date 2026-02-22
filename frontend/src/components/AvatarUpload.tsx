import { useState, useRef } from 'react'
import { Button, Modal, Alert, Spinner } from 'react-bootstrap'
import { toast } from 'react-toastify'
import api from '../api/client'

interface AvatarUploadProps {
  currentAvatar?: string
  onAvatarChange: (avatarUrl: string) => void
}

export const AvatarUpload = ({ currentAvatar, onAvatarChange }: AvatarUploadProps) => {
  const [showModal, setShowModal] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Проверка типа файла
    if (!file.type.startsWith('image/')) {
      toast.error('Пожалуйста, выберите изображение')
      return
    }

    // Проверка размера (5 MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Размер файла не должен превышать 5 MB')
      return
    }

    // Предпросмотр
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0]
    if (!file) return

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/files/upload/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      onAvatarChange(response.data.url)
      toast.success('Аватар успешно загружен')
      setShowModal(false)
      setPreview(null)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки')
    } finally {
      setUploading(false)
    }
  }

  return (
    <>
      <div
        className="avatar-upload-container"
        onClick={() => setShowModal(true)}
        style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          overflow: 'hidden',
          cursor: 'pointer',
          position: 'relative',
        }}
      >
        {currentAvatar ? (
          <img
            src={currentAvatar}
            alt="Avatar"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              background: '#e5e7eb',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '40px',
              color: '#6b7280',
            }}
          >
            👤
          </div>
        )}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'rgba(0,0,0,0.6)',
            color: 'white',
            textAlign: 'center',
            padding: '4px',
            fontSize: '12px',
          }}
        >
          Изменить
        </div>
      </div>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Загрузка аватара</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          <Button
            variant="outline-primary"
            className="w-100 mb-3"
            onClick={() => fileInputRef.current?.click()}
          >
            📁 Выбрать файл
          </Button>

          {preview && (
            <div className="text-center mb-3">
              <img
                src={preview}
                alt="Preview"
                style={{ maxWidth: '200px', borderRadius: '8px' }}
              />
            </div>
          )}

          <Alert variant="info" className="mb-0">
            <small>
              • Максимальный размер: 5 MB<br />
              • Форматы: JPG, PNG, GIF, WebP
            </small>
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Отмена
          </Button>
          <Button
            variant="primary"
            onClick={handleUpload}
            disabled={!preview || uploading}
          >
            {uploading ? (
              <>
                <Spinner as="span" animation="border" size="sm" /> Загрузка...
              </>
            ) : (
              'Загрузить'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  )
}
