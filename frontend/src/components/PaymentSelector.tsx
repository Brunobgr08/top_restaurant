import { UseFormRegister } from 'react-hook-form';
import { OrderFormData } from '@/services/types';
import { Label } from '@/components/ui/label';

interface Props {
  register: UseFormRegister<OrderFormData>;
}

export default function PaymentSelector({ register }: Props) {
  return (
    <div className="space-y-2">
      <Label>Tipo de pagamento:</Label>
      <select
        {...register('payment_type')}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300"
      >
        <option value="manual">Manual</option>
        <option value="online">Online</option>
      </select>
    </div>
  );
}
