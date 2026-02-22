import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Флаг для предотвращения повторных попыток refresh
let isRefreshing = false
// Очередь запросов, ожидающих refresh
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Если ошибка 401 и запрос ещё не повторялся
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Если уже идёт refresh, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refreshToken')

      if (refreshToken) {
        try {
          // Пытаемся обновить токен
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token: newRefreshToken } = response.data

          // Сохраняем новые токены
          localStorage.setItem('token', access_token)
          localStorage.setItem('refreshToken', newRefreshToken)

          // Обновляем заголовок авторизации
          originalRequest.headers.Authorization = `Bearer ${access_token}`

          // Обрабатываем очередь
          processQueue(null, access_token)

          return api(originalRequest)
        } catch (refreshError) {
          // Если refresh не удался, выходим
          processQueue(error as Error, null)
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('userEmail')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // Нет refresh токена, выходим
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('userEmail')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
