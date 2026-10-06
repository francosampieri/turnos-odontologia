import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app

def _is_dev_doc_route(path: str) -> bool:
    return path.startswith(("/docs", "/openapi.json", "/redoc"))


def _settings(monkeypatch, env: str = "development") -> Settings:
    monkeypatch.setenv("ENV", env)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-para-tests-suficientemente-larga-123456")
    return Settings()


@pytest.mark.asyncio
async def test_app_declares_no_routes_outside_api_v1(monkeypatch):
    app = create_app(_settings(monkeypatch))
    for route in app.routes:
        if _is_dev_doc_route(route.path):
            continue
        assert route.path.startswith("/api/v1")


@pytest.mark.asyncio
async def test_get_inexistent_api_route_returns_json_404(monkeypatch):
    app = create_app(_settings(monkeypatch))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ruta-inexistente")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.asyncio
async def test_docs_responds_in_development(monkeypatch):
    app = create_app(_settings(monkeypatch, "development"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_docs_and_openapi_404_in_production(monkeypatch):
    app = create_app(_settings(monkeypatch, "production"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        docs = await client.get("/docs")
        openapi = await client.get("/openapi.json")
    assert docs.status_code == 404
    assert openapi.status_code == 404


@pytest.mark.asyncio
async def test_cors_allowed_origin_returns_exact_origin_without_credentials(monkeypatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-para-tests-suficientemente-larga-123456")
    app = create_app(Settings())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ruta-inexistente", headers={"Origin": "http://b"})
    assert response.headers.get("access-control-allow-origin") == "http://b"
    assert "access-control-allow-credentials" not in response.headers


@pytest.mark.asyncio
async def test_cors_disallowed_origin_receives_no_allow_origin(monkeypatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-para-tests-suficientemente-larga-123456")
    app = create_app(Settings())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ruta-inexistente", headers={"Origin": "http://evil"})
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.asyncio
async def test_unhandled_exception_returns_json_500_without_stack_trace(monkeypatch):
    app = create_app(_settings(monkeypatch))

    @app.get("/api/v1/boom")
    async def boom() -> None:
        raise RuntimeError("detalle-sensible-no-expuesto")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/boom")
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"]
    assert "detalle-sensible-no-expuesto" not in response.text
    assert "Traceback" not in response.text