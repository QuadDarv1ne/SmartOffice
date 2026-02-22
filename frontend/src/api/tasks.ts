import api from './client'

export interface Task {
  task_id: number
  project_id: number
  title: string
  description: string | null
  assigned_to: number | null
  deadline: string | null
  priority: string
  estimated_hours: number | null
  status: string
}

export interface TaskCreate {
  project_id: number
  title: string
  description?: string
  assigned_to?: number
  deadline?: string
  priority?: string
  estimated_hours?: number
  status?: string
}

export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

export const getTasks = async (params?: {
  skip?: number
  limit?: number
  project_id?: number
  assigned_to?: number
  status?: string
}): Promise<PaginatedResponse<Task>> => {
  const response = await api.get<PaginatedResponse<Task>>('/tasks/', { params })
  return response.data
}

export const getTask = async (id: number): Promise<Task> => {
  const response = await api.get<Task>(`/tasks/${id}`)
  return response.data
}

export const createTask = async (data: TaskCreate): Promise<Task> => {
  const response = await api.post<Task>('/tasks/', data)
  return response.data
}

export const updateTask = async (id: number, data: Partial<TaskCreate>): Promise<Task> => {
  const response = await api.put<Task>(`/tasks/${id}`, data)
  return response.data
}

export const deleteTask = async (id: number): Promise<void> => {
  await api.delete(`/tasks/${id}`)
}
