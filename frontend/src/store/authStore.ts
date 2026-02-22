import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  is_active: boolean
  is_admin: boolean
  employee_id?: number
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (token: string, refreshToken: string, userEmail: string) => void
  logout: () => void
  setUser: (user: User) => void
  setLoading: (loading: boolean) => void
  checkAuth: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      login: (token, refreshToken, userEmail) => {
        localStorage.setItem('userEmail', userEmail)
        set({
          token,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
        })
      },

      logout: () => {
        localStorage.removeItem('userEmail')
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      setUser: (user) => set({ user }),

      setLoading: (loading) => set({ isLoading: loading }),

      checkAuth: () => {
        const token = localStorage.getItem('token')
        const refreshToken = localStorage.getItem('refreshToken')
        if (token && refreshToken) {
          set({ 
            token, 
            refreshToken, 
            isAuthenticated: true,
            isLoading: false 
          })
          return true
        }
        set({ isLoading: false })
        return false
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
