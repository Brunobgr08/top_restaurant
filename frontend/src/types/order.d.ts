interface Order {
  id?: number;
  customer_name: string;
  item: string;
  status?: string;
  created_at?: string;
}

interface ApiResponse {
  success: boolean;
  message?: string;
  data?: Order | Order[];
}
