import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import * as assetsApi from './assets'
import type { AssetCreate } from './assets'

export const useAssets = (params?: {
  skip?: number
  limit?: number
  type?: string
  status?: string
}) => {
  return useQuery({
    queryKey: ['assets', params],
    queryFn: () => assetsApi.getAssets(params),
  })
}

export const useAsset = (id: number) => {
  return useQuery({
    queryKey: ['asset', id],
    queryFn: () => assetsApi.getAsset(id),
    enabled: !!id,
  })
}

export const useCreateAsset = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: AssetCreate) => assetsApi.createAsset(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      toast.success('Оборудование успешно добавлено')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при добавлении')
    },
  })
}

export const useUpdateAsset = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<AssetCreate> }) =>
      assetsApi.updateAsset(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      toast.success('Данные обновлены')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при обновлении')
    },
  })
}

export const useDeleteAsset = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => assetsApi.deleteAsset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      toast.success('Оборудование удалено')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при удалении')
    },
  })
}
