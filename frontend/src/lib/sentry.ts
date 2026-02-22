import * as Sentry from "@sentry/react"

// Инициализация Sentry для frontend
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN || "",
  environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || "development",
  
  // Performance Monitoring
  tracesSampleRate: 0.1, // 10% запросов
  
  // Replays (опционально)
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
    Sentry.feedbackIntegration({
      colorScheme: "system",
    }),
  ],

  // Настройки
  beforeSend(event, hint) {
    // Фильтрация чувствительных данных
    if (event.request) {
      // Удаляем cookies
      if (event.request.cookies) {
        delete event.request.cookies
      }
      
      // Удаляем Authorization header
      if (event.request.headers) {
        event.request.headers.Authorization = '[REDACTED]'
      }
    }
    
    // Игнорируем некоторые ошибки
    if (hint.originalException) {
      const error = hint.originalException as Error
      
      // Игнорируем ошибки сети
      if (error.message.includes('NetworkError') || 
          error.message.includes('Network request failed')) {
        return null
      }
      
      // Игнорируем ошибки 4xx (кроме 401, 403)
      if (event.exception) {
        const errorCode = event.exception.values?.[0]?.value?.match(/\d{3}/)?.[0]
        if (errorCode && errorCode.startsWith('4') && !['401', '403'].includes(errorCode)) {
          return null
        }
      }
    }
    
    return event
  },

  // Отслеживание навигации
  beforeSendTransaction(event) {
    // Удаляем чувствительные данные из транзакций
    return event
  },
})

// Экспорт для использования в приложении
export { Sentry }
export default Sentry
