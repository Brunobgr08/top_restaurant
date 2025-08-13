from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from datetime import datetime
from shared.enums import PaymentStatus, PaymentType
from fastapi import HTTPException


class OrderItemCreate(BaseModel):
    item_id: str
    quantity: int = Field(..., gt=0)

    @field_validator('item_id')
    def validar_uuid(cls, v):
        try:
            UUID(v)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="O campo 'item_id' deve ser um UUID válido. Exemplo: '123e4567-e89b-12d3-a456-426614174000'."
            )
        return v

    @field_validator('quantity')
    def validar_quantidade(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=422,
                detail="A quantidade deve ser maior que zero."
            )
        return v

class OrderItemResponse(BaseModel):
    item_id: UUID
    item_name: str
    unit_price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)