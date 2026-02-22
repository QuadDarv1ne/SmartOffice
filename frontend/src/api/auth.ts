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
  token_type: string
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', credentials)
  return response.data
}

export const register = async (data: RegisterData): Promise<any> => {
  const response = await api.post('/auth/register', data)
  return response.data
}

export const getToken = (): string | null => {
  return localStorage.getItem('token')
}

export const setToken = (token: string): void => {
  localStorage.setItem('token', token)
}

export const removeToken = (): void => {
  localStorage.removeItem('token')
}

export const isAuthenticated = (): boolean => {
  return !!getToken()
}
