import api from './client'

export interface Project {
  project_id: number
  name: string
  description: string | null
  start_date: string | null
  end_date: string | null
  status: string
  manager_id: number | null
  budget: number | null
  actual_cost: number | null
}

export interface ProjectCreate {
  name: string
  description?: string
  start_date?: string
  end_date?: string
  status?: string
  manager_id?: number
  budget?: number
}

export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

export const getProjects = async (params?: {
  skip?: number
  limit?: number
  status?: string
}): Promise<PaginatedResponse<Project>> => {
  const response = await api.get<PaginatedResponse<Project>>('/projects/', { params })
  return response.data
}

export const getProject = async (id: number): Promise<Project> => {
  const response = await api.get<Project>(`/projects/${id}`)
  return response.data
}

export const createProject = async (data: ProjectCreate): Promise<Project> => {
  const response = await api.post<Project>('/projects/', data)
  return response.data
}

export const updateProject = async (id: number, data: Partial<ProjectCreate>): Promise<Project> => {
  const response = await api.put<Project>(`/projects/${id}`, data)
  return response.data
}

export const deleteProject = async (id: number): Promise<void> => {
  await api.delete(`/projects/${id}`)
}
