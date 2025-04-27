# FastAPI 프로젝트

이 프로젝트는 Python 3.11을 사용하는 FastAPI 웹 애플리케이션입니다.

## 설치 방법

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

## 실행 방법

1. 개발 서버 실행:

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

2. 웹 브라우저에서 접속:
   - API 문서: http://localhost:8000/docs
   - 대체 API 문서: http://localhost:8000/redoc
   - 메인 페이지: http://localhost:8000

## 프로젝트 구조

```
.
├── app/                    # 애플리케이션 패키지
│   ├── routers/            # API 엔드포인트 라우터
│   ├── models/             # 데이터베이스 모델
│   ├── schemas/            # Pydantic 모델/스키마
│   ├── config.py           # 설정 관리
│   └── settings.py         # 기본 설정 값
├── main.py                 # 애플리케이션 진입점
└── requirements.txt        # 프로젝트 종속성
```
