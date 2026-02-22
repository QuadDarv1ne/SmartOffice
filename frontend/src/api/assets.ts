import api from './client'

export interface Asset {
  asset_id: number
  name: string
  type: string
  serial_number: string | null
  purchase_date: string | null
  purchase_price: number | null
  warranty_until: string | null
  status: string
  notes: string | null
}

export interface AssetCreate {
  name: string
  type: string
  serial_number?: string
  purchase_date?: string
  purchase_price?: number
  warranty_until?: string
  status?: string
  notes?: string
}

export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

export const getAssets = async (params?: {
  skip?: number
  limit?: number
  type?: string
  status?: string
}): Promise<PaginatedResponse<Asset>> => {
  const response = await api.get<PaginatedResponse<Asset>>('/assets/', { params })
  return response.data
}

export const getAsset = async (id: number): Promise<Asset> => {
  const response = await api.get<Asset>(`/assets/${id}`)
  return response.data
}

export const createAsset = async (data: AssetCreate): Promise<Asset> => {
  const response = await api.post<Asset>('/assets/', data)
  return response.data
}

export const updateAsset = async (id: number, data: Partial<AssetCreate>): Promise<Asset> => {
  const response = await api.put<Asset>(`/assets/${id}`, data)
  return response.data
}

export const deleteAsset = async (id: number): Promise<void> => {
  await api.delete(`/assets/${id}`)
}
