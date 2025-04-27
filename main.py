from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import logging
from app.config import settings
from app.routers import api

# 로그 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI 프로젝트 템플릿",
    version="0.1.0",
)

# CORS 설정 - 모든 오리진 허용 및 웹소켓 지원
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")

# 라우터 등록
app.include_router(api.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # 정적 HTML 페이지로 리다이렉트
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 