from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime
from uuid import UUID
from shared.enums import PaymentStatus, PaymentType

class PaymentBase(BaseModel):

    order_id: UUID = Field(..., description="ID do pedido associado")
    amount: float = Field(..., gt=0, description="Valor do pagamento")
    payment_type: PaymentType = Field(
        default=PaymentType.manual,
        description="Tipo de pagamento: 'online' ou 'manual'"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.pending,
        description="Status de pagamento do pedido"
    )

    @validator('amount')
    def round_amount(cls, v):
        return round(v, 2)

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(BaseModel):
    payment_id: UUID
    order_id: UUID
    amount: float
    payment_type: PaymentType
    status: PaymentStatus
    created_at: datetime

    @field_validator('payment_type', mode='before')
    @classmethod
    def extract_payment_type(cls, v):
        # Converte objeto ORM para string
        return getattr(v, 'name', v)

    class Config:
        from_attributes = True