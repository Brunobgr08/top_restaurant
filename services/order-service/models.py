import uuid
from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from shared.enums import PaymentType, PaymentStatus

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    customer_name = Column(String(100), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(Enum(PaymentType, name='payment_type_enum'),nullable=False, default=PaymentType.manual)
    status = Column(Enum(PaymentStatus, name='payment_status_enum'), default=PaymentStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    order_id = Column(String, ForeignKey('orders.order_id', ondelete="CASCADE"), nullable=False)
    item_id = Column(String, nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
