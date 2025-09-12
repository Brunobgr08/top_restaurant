import { MenuItem, OrderFormData, ApiResponse } from './types';

const API_ORDERS = import.meta.env.VITE_API_BASE_ORDERS;
const API_MENU = import.meta.env.VITE_API_BASE_MENU;

export async function fetchMenu(): Promise<MenuItem[]> {
  try {
    const url = `${API_MENU}/api/v1/menu`;

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
