import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app


def _settings(monkeypatch, env: str = "development") -> Settings:
    monkeypatch.setenv("ENV", env)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-para-tests-suficientemente-larga-123456")
    return Settings()


@pytest.mark.asyncio
async def test_health_is_public_and_ok_when_database_available(monkeypatch):
    async def _check_ok() -> bool:
        return True

    monkeypatch.setattr("app.api.routers.health.check_database", _check_ok)
    app = create_app(_settings(monkeypatch))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


@pytest.mark.asyncio
async def test_health_is_not_ok_when_database_check_fails(monkeypatch):
    async def _check_ko() -> bool:
        raise OSError("base caída")

    monkeypatch.setattr("app.api.routers.health.check_database", _check_ko)
    app = create_app(_settings(monkeypatch))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "error"