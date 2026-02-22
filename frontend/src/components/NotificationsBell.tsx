import { useEffect } from 'react'
import { Dropdown, Badge, Button } from 'react-bootstrap'
import { useWebSocket } from '../hooks/useWebSocket'
import { useNotificationsStore } from '../store/notificationsStore'
import { toast } from 'react-toastify'

export const NotificationsBell = () => {
  const { notifications, unreadCount, addNotification, markAllAsRead } = useNotificationsStore()

  const handleNotification = (notification: any) => {
    addNotification(notification)
    
    // Показываем toast
    toast.info(`${notification.title}: ${notification.message}`, {
      icon: '🔔',
      autoClose: 5000,
    })
  }

  const { isConnected, joinRoom } = useWebSocket({
    onNotification: handleNotification,
    onConnect: () => console.log('WebSocket connected for notifications'),
  })

  // Подписка на комнату проектов при подключении
  useEffect(() => {
    if (isConnected) {
      joinRoom('projects:all')
      joinRoom('employees:all')
    }
  }, [isConnected, joinRoom])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const getNotificationIcon = (type: string) => {
    const icons: Record<string, string> = {
      task_created: '📝',
      task_assigned: '👤',
      employee_added: '👥',
      project_updated: '📊',
      system: '⚙️',
    }
    return icons[type] || '🔔'
  }

  return (
    <Dropdown>
      <Dropdown.Toggle variant="light" id="notifications-dropdown">
        <Badge bg={unreadCount > 0 ? 'danger' : 'secondary'} pill>
          {unreadCount}
        </Badge>
        <i className="bi bi-bell ms-2"></i>
      </Dropdown.Toggle>

      <Dropdown.Menu align="end" style={{ width: '350px' }}>
        <Dropdown.Header className="d-flex justify-content-between align-items-center">
          <span>Уведомления</span>
          <Badge bg={isConnected ? 'success' : 'secondary'}>{isConnected ? 'Online' : 'Offline'}</Badge>
        </Dropdown.Header>

        <Dropdown.Divider />

        {notifications.length === 0 ? (
          <Dropdown.ItemText className="text-center text-muted py-3">
            Нет уведомлений
          </Dropdown.ItemText>
        ) : (
          <>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {notifications.map((notification) => (
                <Dropdown.Item
                  key={notification.id}
                  onClick={() => {}}
                  className={notification.read ? 'text-muted' : 'fw-bold'}
                >
                  <div className="d-flex justify-content-between">
                    <span>{getNotificationIcon(notification.notification_type)}</span>
                    <small className="text-muted">{formatTime(notification.timestamp)}</small>
                  </div>
                  <div className="mt-1">{notification.title}</div>
                  <small className="text-muted">{notification.message}</small>
                </Dropdown.Item>
              ))}
            </div>

            <Dropdown.Divider />

            <Dropdown.Item onClick={markAllAsRead} className="text-center">
              <Button variant="link" size="sm">
                Отметить все как прочитанные
              </Button>
            </Dropdown.Item>
          </>
        )}
      </Dropdown.Menu>
    </Dropdown>
  )
}
