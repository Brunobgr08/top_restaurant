from sqlalchemy import Column, String, Numeric, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
from database import Base
import uuid


class MenuItem(Base):
    __tablename__ = 'menu_items'

    item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MenuItem(name={self.name}, price={self.price}, available={self.available})>"
