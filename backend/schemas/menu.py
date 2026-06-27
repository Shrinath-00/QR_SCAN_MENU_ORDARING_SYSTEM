from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class MenuItemBase(BaseModel):
    name: str
    price: float

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemSchema(MenuItemBase):
    model_config = ConfigDict(from_attributes=True)

class MenuCategorySchema(BaseModel):
    id: str          # maps to DB cat_id
    name: str
    emoji: str = ""
    description: Optional[str] = ""
    items: List[MenuItemSchema] = []

    model_config = ConfigDict(from_attributes=True)

class MenuResponse(BaseModel):
    categories: List[MenuCategorySchema]
