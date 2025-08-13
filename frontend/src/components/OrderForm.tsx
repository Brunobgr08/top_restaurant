import { useForm, useFieldArray, useWatch } from 'react-hook-form';
import { useEffect, useState } from 'react';
import { useMenu } from '@/hooks/useMenu';
import { createOrder } from '@/services/api';
import { OrderFormData } from '@/services/types';
import OrderItem from './OrderItem';
import PaymentSelector from './PaymentSelector';
import OrderSummary from './OrderSummary';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

export default function OrderForm() {
  const { menu, fetchMenu } = useMenu();

  const {
    control,
    handleSubmit,
    register,
    formState: { errors },
    reset,
  } = useForm<OrderFormData>({
    defaultValues: {
      customer_name: '',
      items: [{ item_id: '', quantity: 1 }],
      payment_type: 'manual',
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMenu();
  }, []);

  const onSubmit = async (data: OrderFormData) => {
    setIsLoading(true);
    const result = await createOrder(data);
    if (result.success) {
      toast.success('Pedido criado com sucesso!');
      reset();
    } else {
      toast.error(`Erro: ${result.message}`);
    }
    setIsLoading(false);
  };

  const watchedItems = useWatch({ control, name: 'items' });

  const watchedCustomerName = useWatch({ control, name: 'customer_name' });

  const watchedPaymentType = useWatch({ control, name: 'payment_type' });

  const realTimeData = {
    customer_name: watchedCustomerName || '',
    items: watchedItems || [],
    payment_type: watchedPaymentType || 'manual',
  };

  return (
    <motion.form
      className="space-y-6"
      onSubmit={handleSubmit(onSubmit)}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-2">
        <Label htmlFor="name">Seu nome:</Label>
        <Input id="name" {...register('customer_name', { required: true })} />
        <div className="min-h-[20px] text-sm text-red-600">
          {errors.customer_name && <span>Nome é obrigatório.</span>}
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Itens do Pedido</h3>
        {fields.map((field, index) => (
          <OrderItem
            key={field.id}
            index={index}
            control={control}
            register={register}
            menu={menu}
            remove={() => remove(index)}
            error={errors.items?.[index]}
          />
        ))}
        <Button
          type="button"
          variant="outline"
          onClick={() => append({ item_id: '', quantity: 1 })}
        >
          + Adicionar Item
        </Button>
      </div>

      <Separator />

      <PaymentSelector register={register} />

      <OrderSummary data={realTimeData} menu={menu} />

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} Enviar Pedido
      </Button>
    </motion.form>
  );
}
