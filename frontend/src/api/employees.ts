import api from './client'

export interface Employee {
  employee_id: number
  full_name: string
  email: string | null
  phone: string | null
  hire_date: string
  department_id: number
  position_id: number
  manager_id: number | null
  termination_date: string | null
}

export interface EmployeeCreate {
  full_name: string
  email?: string
  phone?: string
  hire_date: string
  department_id: number
  position_id: number
  manager_id?: number
}

export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

export const getEmployees = async (params?: {
  skip?: number
  limit?: number
  department_id?: number
  search?: string
}): Promise<PaginatedResponse<Employee>> => {
  const response = await api.get<PaginatedResponse<Employee>>('/employees/', { params })
  return response.data
}

export const getEmployee = async (id: number): Promise<Employee> => {
  const response = await api.get<Employee>(`/employees/${id}`)
  return response.data
}

export const createEmployee = async (data: EmployeeCreate): Promise<Employee> => {
  const response = await api.post<Employee>('/employees/', data)
  return response.data
}

export const updateEmployee = async (id: number, data: Partial<EmployeeCreate>): Promise<Employee> => {
  const response = await api.put<Employee>(`/employees/${id}`, data)
  return response.data
}

export const deleteEmployee = async (id: number): Promise<void> => {
  await api.delete(`/employees/${id}`)
}
