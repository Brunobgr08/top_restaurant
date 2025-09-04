import { MenuItem, OrderFormData, ApiResponse } from './types';

// Detectar ambiente - desenvolvimento ou produção
const isDevelopment = import.meta.env.MODE === 'development';

// Configurar URLs base baseadas no ambiente
const getBaseURL = (service: 'orders' | 'menu') => {
  if (isDevelopment) {
    // Em desenvolvimento, usar variáveis de ambiente com URLs completas
    return service === 'orders'
      ? import.meta.env.VITE_API_BASE_ORDERS
      : import.meta.env.VITE_API_BASE_MENU;
  } else {
    // Em produção, usar caminhos relativos (proxy do Nginx)
    return `/${service}`;
  }
};

const API_ORDERS = getBaseURL('orders');
const API_MENU = getBaseURL('menu');

export async function fetchMenu(): Promise<MenuItem[]> {
  try {
    const url = isDevelopment
      ? `${API_MENU}/api/v1/menu`
      : `/api/v1/menu`; // Em produção, o proxy do Nginx já inclui o caminho base

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
  const url = isDevelopment
    ? `${API_ORDERS}/api/v1/orders`
    : `/api/v1/orders`; // Em produção, o proxy do Nginx já inclui o caminho base

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
