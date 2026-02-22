import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import * as tasksApi from './tasks'
import type { TaskCreate } from './tasks'

export const useTasks = (params?: {
  skip?: number
  limit?: number
  project_id?: number
  assigned_to?: number
  status?: string
}) => {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: () => tasksApi.getTasks(params),
  })
}

export const useTask = (id: number) => {
  return useQuery({
    queryKey: ['task', id],
    queryFn: () => tasksApi.getTask(id),
    enabled: !!id,
  })
}

export const useCreateTask = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: TaskCreate) => tasksApi.createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Задача успешно создана')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при создании задачи')
    },
  })
}

export const useUpdateTask = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TaskCreate> }) =>
      tasksApi.updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Задача обновлена')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при обновлении')
    },
  })
}

export const useDeleteTask = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => tasksApi.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Задача удалена')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при удалении')
    },
  })
}
