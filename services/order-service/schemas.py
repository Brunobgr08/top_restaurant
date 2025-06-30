from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID
from shared.enums import PaymentStatus, PaymentType


class OrderItemCreate(BaseModel):
    item_id: UUID
    quantity: int = Field(..., gt=0)

class OrderItemResponse(BaseModel):
    item_id: UUID
    item_name: str
    unit_price: float
    quantity: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    items: list[OrderItemCreate]
    payment_type: PaymentType = Field(
        default=PaymentType.manual,
        description="Tipo de pagamento: 'online' ou 'manual'"
    )

class OrderResponse(BaseModel):
    order_id: UUID
    customer_name: str
    total_price: float
    payment_type: PaymentType
    status: PaymentStatus
    created_at: datetime
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True