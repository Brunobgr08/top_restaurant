import { Toaster } from 'sonner';
import { Card, CardContent } from '@/components/ui/card';
import OrderForm from '@/components/OrderForm';

export default function App() {
  return (
    <>
      <Toaster position="top-center" richColors />
      <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
        <Card className="w-full max-w-2xl shadow-md">
          <CardContent>
            <h1 className="text-2xl font-bold text-center mb-4">Realizar Pedido</h1>
            <OrderForm />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
