import { create } from 'zustand'

interface Notification {
  id: string
  type: string
  notification_type: string
  title: string
  message: string
  data: Record<string, unknown>
  timestamp: string
  read: boolean
}

interface NotificationsState {
  notifications: Notification[]
  unreadCount: number
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'read'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  clearNotifications: () => void
  removeNotification: (id: string) => void
}

export const useNotificationsStore = create<NotificationsState>((set) => ({
  notifications: [],
  unreadCount: 0,

  addNotification: (notification) =>
    set((state) => {
      const newNotification: Notification = {
        ...notification,
        id: `${notification.notification_type}-${Date.now()}`,
        read: false,
      }
      
      // Сохраняем последние 50 уведомлений
      const updatedNotifications = [newNotification, ...state.notifications].slice(0, 50)
      
      return {
        notifications: updatedNotifications,
        unreadCount: state.unreadCount + 1,
      }
    }),

  markAsRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    })),

  clearNotifications: () => set({ notifications: [], unreadCount: 0 }),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}))
