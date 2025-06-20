from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from shared.enums import PaymentType as PaymentTypeEnum, PaymentStatus

class PaymentTypeModel(Base):
    __tablename__ = 'payment_types'

    type_id = Column(String, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False, unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type_id = Column(String, ForeignKey('payment_types.type_id', ondelete="RESTRICT"), nullable=False, default='manual')
    status = Column(Enum(PaymentStatus, name='payment_status_enum'), nullable=False, default=PaymentStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    payment_type = relationship("PaymentTypeModel", lazy="joined")  # Carrega automaticamente

    @property
    def payment_type_enum(self) -> PaymentTypeEnum:
        """Retorna o Enum correspondente ao payment_type_id"""
        try:
            return PaymentTypeEnum(self.payment_type.name)
        except ValueError as e:
            return PaymentTypeEnum.manual  # Fallback seguro

    @property
    def payment_type_name(self):
        """Retorna o nome do tipo de pagamento como string"""
        return self.payment_type.name if self.payment_type else None