from uuid import UUID
from pydantic import BaseModel, Field, field_validator, validator, ConfigDict
from datetime import datetime
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

    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        return round(v, 2)

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str
    order_id: str
    amount: float
    payment_type: str
    status: str
    created_at: datetime

    @field_validator('payment_type', mode='before')
    @classmethod
    def extract_payment_type(cls, v):
        return getattr(v, 'name', v)

class PaymentConfirmResponse(BaseModel):
    message: str
    payment_id: str
    status: str