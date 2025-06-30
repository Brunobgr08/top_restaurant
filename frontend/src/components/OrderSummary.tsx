import { MenuItem, OrderFormData } from '@/services/types';
import { Card, CardContent } from '@/components/ui/card';

interface Props {
  data: OrderFormData;
  menu: MenuItem[];
}

export default function OrderSummary({ data, menu }: Props) {
  const getItemDetails = (id: string) => menu.find((m) => m.item_id === id);

  const total = data.items.reduce((acc, item) => {
    const found = getItemDetails(item.item_id);
    return acc + (found ? found.price * item.quantity : 0);
  }, 0);

  return (
    <Card className="mt-4 shadow-sm bg-muted">
      <CardContent className="space-y-3 p-6">
        <h3 className="font-semibold text-xl">Resumo do Pedido</h3>
        <ul className="text-sm text-muted-foreground">
          {data.items.map((item, idx) => {
            const details = getItemDetails(item.item_id);
            if (!details) return null;
            return (
              <li key={idx} className="flex justify-between">
                <span>{details.name} x {item.quantity}</span>
                <span className="font-medium">R$ {(details.price * item.quantity).toFixed(2)}</span>
              </li>
            );
          })}
        </ul>
        <hr />
        <div className="text-right font-bold text-base">
          Total: R$ {total.toFixed(2)}
        </div>
      </CardContent>
    </Card>
  );
}
