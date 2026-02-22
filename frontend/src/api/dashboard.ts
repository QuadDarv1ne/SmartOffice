import api from './client'

export interface DashboardStats {
  employees: {
    total: number
    active: number
  }
  departments: number
  projects: {
    total: number
    active: number
  }
  tasks: {
    total: number
    pending: number
    completed: number
  }
  assets: {
    total: number
    available: number
    in_use: number
  }
}

export interface ChartData {
  name: string
  count: number
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get<DashboardStats>('/dashboard/stats')
  return response.data
}

export const getEmployeesByDepartment = async (): Promise<ChartData[]> => {
  const response = await api.get<ChartData[]>('/dashboard/employees-by-department')
  return response.data
}

export const getTasksByStatus = async (): Promise<ChartData[]> => {
  const response = await api.get<ChartData[]>('/dashboard/tasks-by-status')
  return response.data
}

export const getProjectsByStatus = async (): Promise<ChartData[]> => {
  const response = await api.get<ChartData[]>('/dashboard/projects-by-status')
  return response.data
}
