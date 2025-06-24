from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None

class MenuItemResponse(MenuItemBase):
    item_id: UUID

    class Config:
        from_attributes = True
