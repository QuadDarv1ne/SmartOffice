import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark'

interface ThemeState {
  theme: Theme
  isDark: boolean
  
  // Actions
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      isDark: false,

      setTheme: (theme) => {
        const isDark = theme === 'dark'
        document.documentElement.setAttribute('data-theme', theme)
        document.documentElement.style.colorScheme = theme
        set({ theme, isDark })
      },

      toggleTheme: () => {
        const newTheme = get().theme === 'light' ? 'dark' : 'light'
        get().setTheme(newTheme)
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

// Initialize theme on load
if (typeof window !== 'undefined') {
  const savedTheme = localStorage.getItem('theme-storage')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (savedTheme) {
    try {
      const parsed = JSON.parse(savedTheme)
      const theme = parsed.state?.theme || 'light'
      document.documentElement.setAttribute('data-theme', theme)
      document.documentElement.style.colorScheme = theme
    } catch {
      const theme = prefersDark ? 'dark' : 'light'
      document.documentElement.setAttribute('data-theme', theme)
      document.documentElement.style.colorScheme = theme
    }
  } else {
    const theme = prefersDark ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.style.colorScheme = theme
  }
}
