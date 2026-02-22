import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import * as departmentsApi from './departments'
import type { DepartmentCreate } from './departments'

export const useDepartments = () => {
  return useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentsApi.getDepartments(),
  })
}

export const useCreateDepartment = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: DepartmentCreate) => departmentsApi.createDepartment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
      toast.success('Отдел успешно создан')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при создании отдела')
    },
  })
}

export const useDeleteDepartment = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => departmentsApi.deleteDepartment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
      toast.success('Отдел удалён')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при удалении отдела')
    },
  })
}
