from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID
from shared.enums import PaymentStatus, PaymentType

class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1)
    item_name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    status: PaymentStatus = Field(
        default=PaymentStatus.pending,
        description="Status de pagamento do pedido"
    )
    payment_type: PaymentType = Field(
        default=PaymentType.manual,
        description="Tipo de pagamento: 'online' ou 'manual'"
    )

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: UUID
    status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True