import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import * as projectsApi from './projects'
import type { ProjectCreate } from './projects'

export const useProjects = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => projectsApi.getProjects(params),
  })
}

export const useProject = (id: number) => {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.getProject(id),
    enabled: !!id,
  })
}

export const useCreateProject = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: ProjectCreate) => projectsApi.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Проект успешно создан')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при создании проекта')
    },
  })
}

export const useUpdateProject = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProjectCreate> }) =>
      projectsApi.updateProject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Проект обновлён')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при обновлении')
    },
  })
}

export const useDeleteProject = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => projectsApi.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Проект удалён')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при удалении')
    },
  })
}
