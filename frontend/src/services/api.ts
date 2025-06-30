import { MenuItem, OrderFormData, ApiResponse } from './types';

const API_ORDERS = import.meta.env.VITE_API_BASE_ORDERS;
const API_MENU = import.meta.env.VITE_API_BASE_MENU;

export async function fetchMenu(): Promise<MenuItem[]> {
  try {
    const response = await fetch(`${API_MENU}/api/v1/menu`);
    const contentType = response.headers.get('content-type');

    if (!response.ok || !contentType?.includes('application/json')) {
      throw new Error('Resposta inválida do servidor');
    }

    const data = await response.json();
    // console.log('Menu data:', data);
    return data;
  } catch (err) {
    console.error('Erro ao buscar menu:', err);
  }

  return [];
}

export async function createOrder(data: OrderFormData): Promise<ApiResponse> {
  const res = await fetch(`${API_ORDERS}/api/v1/orders`, {
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
