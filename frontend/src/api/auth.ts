import api from './client'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  employee_id?: number
  is_admin?: boolean
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', credentials)
  return response.data
}

export const register = async (data: RegisterData): Promise<any> => {
  const response = await api.post('/auth/register', data)
  return response.data
}

export const refreshToken = async (refreshToken: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  })
  return response.data
}

export const logout = async (): Promise<void> => {
  try {
    await api.post('/auth/logout')
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userEmail')
  }
}

export const getToken = (): string | null => {
  return localStorage.getItem('token')
}

export const getRefreshToken = (): string | null => {
  return localStorage.getItem('refreshToken')
}

export const setToken = (token: string): void => {
  localStorage.setItem('token', token)
}

export const setRefreshToken = (token: string): void => {
  localStorage.setItem('refreshToken', token)
}

export const removeToken = (): void => {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
}

export const isAuthenticated = (): boolean => {
  return !!getToken()
}
