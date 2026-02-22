import api from './client'

export interface Department {
  department_id: number
  name: string
  manager_id: number | null
}

export interface DepartmentCreate {
  name: string
  manager_id?: number
}

export const getDepartments = async (): Promise<Department[]> => {
  const response = await api.get<Department[]>('/departments/')
  return response.data
}

export const createDepartment = async (data: DepartmentCreate): Promise<Department> => {
  const response = await api.post<Department>('/departments/', data)
  return response.data
}

export const deleteDepartment = async (id: number): Promise<void> => {
  await api.delete(`/departments/${id}`)
}
