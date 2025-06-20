from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    available: Optional[bool]

class MenuItemResponse(MenuItemBase):
    item_id: UUID

    class Config:
        from_attributes = True
