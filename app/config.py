import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from app import settings as app_settings

# .env 파일이 있다면 로드 시도
try:
    load_dotenv()
except Exception:
    pass

class Settings(BaseSettings):
    API_V1_STR: str = os.getenv("API_V1_STR", app_settings.API_V1_STR)
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", app_settings.PROJECT_NAME)
    DEBUG: bool = os.getenv("DEBUG", str(app_settings.DEBUG)).lower() == "true"
    
    # 음성 API 설정 추가
    VITO_CLIENT_ID: str = os.getenv("VITO_CLIENT_ID", app_settings.VITO_CLIENT_ID)
    VITO_CLIENT_SECRET: str = os.getenv("VITO_CLIENT_SECRET", app_settings.VITO_CLIENT_SECRET)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 