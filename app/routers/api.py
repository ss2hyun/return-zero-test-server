from fastapi import APIRouter
from app.routers import items, streaming

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

# 하위 라우터 포함
router.include_router(items.router)
router.include_router(streaming.router)

@router.get("/health-check")
async def health_check():
    return {"status": "healthy"} 