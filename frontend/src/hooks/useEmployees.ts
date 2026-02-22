import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import * as employeesApi from './employees'
import type { Employee, EmployeeCreate } from './employees'

export const useEmployees = (params?: {
  skip?: number
  limit?: number
  department_id?: number
  search?: string
}) => {
  return useQuery({
    queryKey: ['employees', params],
    queryFn: () => employeesApi.getEmployees(params),
  })
}

export const useEmployee = (id: number) => {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeesApi.getEmployee(id),
    enabled: !!id,
  })
}

export const useCreateEmployee = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: EmployeeCreate) => employeesApi.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      toast.success('Сотрудник успешно добавлен')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при создании сотрудника')
    },
  })
}

export const useUpdateEmployee = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<EmployeeCreate> }) =>
      employeesApi.updateEmployee(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      toast.success('Данные сотрудника обновлены')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при обновлении')
    },
  })
}

export const useDeleteEmployee = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => employeesApi.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      toast.success('Сотрудник удалён')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при удалении')
    },
  })
}
