"""
애플리케이션 설정 값을 관리하는 모듈입니다.
.env 파일을 사용할 수 없는 경우 이 파일에서 설정값을 직접 변경할 수 있습니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 애플리케이션 설정
DEBUG = os.getenv("DEBUG", "True") == "True"
PROJECT_NAME = os.getenv("PROJECT_NAME", "FastAPI 프로젝트")
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

# 음성 API 설정
VITO_CLIENT_ID = os.getenv("VITO_CLIENT_ID", "vito_client_id")
VITO_CLIENT_SECRET = os.getenv("VITO_CLIENT_SECRET", "vito_client_secret") 