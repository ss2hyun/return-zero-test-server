from pydantic import BaseModel, Field
from typing import Optional


class ItemBase(BaseModel):
    title: str = Field(..., description="아이템 제목")
    description: Optional[str] = Field(None, description="아이템 설명")


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int = Field(..., description="아이템 ID")

    model_config = {
        "from_attributes": True
    } 