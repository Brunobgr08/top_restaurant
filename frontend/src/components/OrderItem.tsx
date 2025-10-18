import { Controller, FieldError } from 'react-hook-form';
import { MenuItem } from '@/services/types';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

interface Props {
  index: number;
  control: any;
  register: any;
  menu: MenuItem[];
  remove: () => void;
  error?: { item_id?: FieldError; quantity?: FieldError };
}

export default function OrderItem({ index, control, register, menu, remove, error }: Props) {
  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-6 gap-4 items-center bg-gray-50 p-4 rounded-md shadow"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="col-span-1 md:col-span-3 space-y-1">
        <Label>Item:</Label>
        <Controller
          name={`items.${index}.item_id` as const}
          control={control}
          rules={{ required: true }}
          render={({ field }) => (
            <select
              {...field}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300"
            >
              <option value="">Selecione um item</option>
              {menu.map((item) => (
                <option key={item.item_id} value={item.item_id}>
                  {item.name} - R$ {item.price.toFixed(2)}
                </option>
              ))}
            </select>
          )}
        />
        <div className="min-h-[20px] text-sm text-red-600">
          {error?.item_id && <span>Item obrigatório.</span>}
        </div>
      </div>

      <div className="col-span-1 md:col-span-2 space-y-1">
        <Label>Quantidade:</Label>
        <Input
          type="number"
          min={1}
          {...register(`items.${index}.quantity` as const, { required: true, min: 1 })}
        />
        <div className="min-h-[20px] text-sm text-red-600">
          {error?.quantity && <span>Informe uma quantidade válida.</span>}
        </div>
      </div>

      <div className="col-span-1 flex items-end">
        <Button type="button" variant="destructive" onClick={remove} className="w-full">
          Remover
        </Button>
      </div>
    </motion.div>
  );
}
