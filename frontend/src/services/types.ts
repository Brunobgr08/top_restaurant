export interface MenuItem {
  item_id: string;
  name: string;
  price: number;
}

export interface OrderItemInput {
  item_id: string;
  quantity: number;
}

export interface OrderFormData {
  customer_name: string;
  items: OrderItemInput[];
  payment_type: 'manual' | 'online';
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  data?: any;
}
