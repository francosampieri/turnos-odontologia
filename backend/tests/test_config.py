import pytest

from app.core.config import Settings


def test_settings_cors_origins_parses_to_exact_list(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b")
    monkeypatch.setenv("ENV", "development")
    settings = Settings()
    assert settings.cors_origins == ["http://a", "http://b"]


def test_settings_env_development_accepted(monkeypatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-real-de-desarrollo-suficientemente-larga")
    settings = Settings()
    assert settings.env == "development"


def test_settings_env_production_accepted(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-real-de-produccion-suficientemente-larga")
    settings = Settings()
    assert settings.env == "production"


def test_settings_production_with_empty_secret_raises(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "http://a")
    monkeypatch.setenv("JWT_SECRET_KEY", "")
    with pytest.raises(RuntimeError):
        Settings()


def test_settings_production_with_example_secret_raises(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "http://a")
    monkeypatch.setenv("JWT_SECRET_KEY", "cambiar-en-produccion")
    with pytest.raises(RuntimeError):
        Settings()


def test_settings_development_with_example_secret_is_accepted(monkeypatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://a")
    monkeypatch.setenv("JWT_SECRET_KEY", "cambiar-en-produccion")
    settings = Settings()
    assert settings.env == "development"