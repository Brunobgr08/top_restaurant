import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime
from database import Base
from datetime import datetime
from shared.enums import PaymentType, PaymentStatus

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    customer_name = Column(String(100), nullable=False)
    item_id = Column(UUID(as_uuid=True), nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(Enum(PaymentType, name='payment_type_enum'),nullable=False, default=PaymentType.manual)
    status = Column(Enum(PaymentStatus, name='payment_status_enum'), default=PaymentStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
