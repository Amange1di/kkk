import axios from 'axios';

const API_URL ='https://kkk-fwjw.onrender.com/api';

// Создаём отдельный экземпляр axios с интерцептором для токена
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Интерцептор для автоматического добавления токена
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Настройка axios по умолчанию (для запросов вне API)
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export interface Asset {
  id: number;
  asset_tag: string;
  name: string;
  asset_type: string;
  status: string;
  current_location?: any;
  assigned_to?: any;
  auditor?: string;
  auditor_user?: any;
  auditor_user_id?: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_price?: string;
}

export interface Location {
  id: number;
  name: string;
  location_type: string;
  building?: string;
  floor?: string;
  room_number?: string;
}

export interface AssetType {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  assets_count?: number;
}

export interface TransferHistory {
  id: number;
  asset: any;
  transfer_type: string;
  from_location?: any;
  to_location?: any;
  transfer_date: string;
}

export const assetsApi = {
  getAll: (params?: any) => apiClient.get('/assets/', { params }),
  getById: (id: number) => apiClient.get(`/assets/${id}/`),
  create: (data: Partial<Asset>) => apiClient.post('/assets/', data),
  update: (id: number, data: Partial<Asset>) => apiClient.put(`/assets/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/assets/${id}/`),
  checkout: (id: number, data: any) => apiClient.post(`/assets/${id}/checkout/`, data),
  checkin: (id: number, data: any) => apiClient.post(`/assets/${id}/checkin/`, data),
  transfer: (id: number, data: any) => apiClient.post(`/assets/${id}/transfer/`, data),
  getQrCode: (id: number) => apiClient.get(`/assets/${id}/qr_code/`),
  scan: (assetTag: string) => apiClient.post('/assets/scan/', { asset_tag: assetTag }),
};

export const locationsApi = {
  getAll: (params?: any) => apiClient.get('/locations/', { params }),
  getById: (id: number) => apiClient.get(`/locations/${id}/`),
  create: (data: Partial<Location>) => apiClient.post('/locations/', data),
  update: (id: number, data: Partial<Location>) => apiClient.put(`/locations/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/locations/${id}/`),
};

export const reportsApi = {
  exportAssets: (format: string, params?: any) => 
    apiClient.get(`/reports/export-assets/`, { 
      params: { ...params, format },
      responseType: 'blob'
    }),
  getSummary: () => apiClient.get('/reports/assets-summary/'),
  getAuditLogs: (params?: any) => apiClient.get('/reports/auditlogs/', { params }),
};

export const assetTypesApi = {
  getAll: (params?: any) => apiClient.get('/assets/types/', { params }),
  getById: (id: number) => apiClient.get(`/assets/types/${id}/`),
  create: (data: Partial<AssetType>) => apiClient.post('/assets/types/', data),
  update: (id: number, data: Partial<AssetType>) => apiClient.put(`/assets/types/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/assets/types/${id}/`),
};


