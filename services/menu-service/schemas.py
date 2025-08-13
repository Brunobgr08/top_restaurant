from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    available: bool = Field(default=True)

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    available: Optional[bool] = Field(default=None)

class MenuItemResponse(MenuItemBase):
    item_id: str

    model_config = ConfigDict(from_attributes=True)
