from fastapi import APIRouter, HTTPException, Path, Body
from typing import List

from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

# 메모리 기반 아이템 저장소 (임시용)
items_db = {}
next_id = 1


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate = Body(...)):
    """
    새로운 아이템을 생성합니다.
    """
    global next_id
    item_dict = item.model_dump()
    item_id = next_id
    next_id += 1
    
    item_with_id = {**item_dict, "id": item_id}
    items_db[item_id] = item_with_id
    
    return item_with_id


@router.get("/", response_model=List[ItemResponse])
async def read_items():
    """
    모든 아이템을 조회합니다.
    """
    return list(items_db.values())


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int = Path(..., description="조회할 아이템의 ID")):
    """
    특정 아이템을 조회합니다.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return items_db[item_id]


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int = Path(..., description="업데이트할 아이템의 ID"),
    item: ItemCreate = Body(...)
):
    """
    특정 아이템을 업데이트합니다.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = item.model_dump()
    items_db[item_id] = {**item_dict, "id": item_id}
    
    return items_db[item_id]


@router.delete("/{item_id}", response_model=dict)
async def delete_item(item_id: int = Path(..., description="삭제할 아이템의 ID")):
    """
    특정 아이템을 삭제합니다.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    
    return {"message": "Item successfully deleted"} 