from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

EXAMPLE_JWT_SECRET = "cambiar-en-produccion"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    env: str = "development"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    jwt_secret_key: str = EXAMPLE_JWT_SECRET

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def require_real_jwt_secret_in_production(self) -> "Settings":
        if self.env == "production" and (
            not self.jwt_secret_key or self.jwt_secret_key == EXAMPLE_JWT_SECRET
        ):
            raise RuntimeError(
                "JWT_SECRET_KEY debe configurarse con un secreto real en ENV=production "
                f"(el valor de ejemplo '{EXAMPLE_JWT_SECRET}' no es aceptable)."
            )
        return self