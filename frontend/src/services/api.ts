import { MenuItem, OrderFormData, ApiResponse } from './types';

const getBaseURL = (service: 'orders' | 'menu') => {
  console.log('API_ORDERS:', (window as any)._env_?.VITE_API_BASE_ORDERS);
  console.log('API_MENU:', (window as any)._env_?.VITE_API_BASE_MENU);

  const ordersUrl =
    import.meta.env.VITE_API_BASE_ORDERS ||
    (window as any)._env_?.VITE_API_BASE_ORDERS ||
    'http://menu-service-production-e4e3.up.railway.app';

  const menuUrl = import.meta.env.VITE_API_BASE_MENU || (window as any)._env_?.VITE_API_BASE_MENU;

  return service === 'orders' ? ordersUrl : menuUrl;
};

const API_ORDERS = getBaseURL('orders');
const API_MENU = getBaseURL('menu');

console.log('API_ORDERS:', API_ORDERS);
console.log('API_MENU:', API_MENU);

export async function fetchMenu(): Promise<MenuItem[]> {
  try {
    const url = `${API_MENU}/api/v1/menu`;

    console.log('URL:', url);

    const response = await fetch(url);
    const contentType = response.headers.get('content-type');

    if (!response.ok || !contentType?.includes('application/json')) {
      throw new Error('Resposta inválida do servidor');
    }

    const data = await response.json();
    return data;
  } catch (err) {
    console.error('Erro ao buscar menu:', err);
  }

  return [];
}

export async function createOrder(data: OrderFormData): Promise<ApiResponse> {
  const url = `${API_ORDERS}/api/v1/orders`;

  console.log('URL:', url);

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  const json = await res.json();
  return {
    success: res.ok,
    message: json?.detail || '',
    data: json,
  };
}
