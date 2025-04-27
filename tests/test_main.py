from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    """
    메인 경로 테스트
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """
    헬스 체크 엔드포인트 테스트
    """
    response = client.get("/api/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 