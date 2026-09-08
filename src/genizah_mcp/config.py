"""Operator-only configuration validation."""

from urllib.parse import urlsplit, urlunsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GENIZAH_MCP_", extra="ignore", populate_by_name=True
    )

    api_base: str = Field(default="https://genizahsearch.com", validation_alias="GENIZAH_API_BASE")
    rpm: int = Field(default=96, ge=1, le=120)
    burst: int = Field(default=5, ge=1, le=10)
    default_text_cap: int = Field(default=4000, ge=100, le=10000)
    max_tool_results: int = Field(default=100, ge=1, le=100)
    connect_timeout: float = Field(default=10, gt=0)
    search_timeout: float = Field(default=320, gt=0)
    browse_timeout: float = Field(default=30, gt=0)
    parallels_timeout: float = Field(default=320, gt=0)
    log_level: str = "INFO"
    allow_insecure_localhost: bool = False

    @field_validator("api_base")
    @classmethod
    def normalize_base(cls, value: str) -> str:
        parts = urlsplit(value)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("GENIZAH_API_BASE must be an absolute HTTP(S) URL")
        if parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError("GENIZAH_API_BASE must not include userinfo, query, or fragment")
        return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))

    @model_validator(mode="after")
    def reject_insecure_nonloopback(self) -> "Settings":
        parts = urlsplit(self.api_base)
        loopback = parts.hostname in {"localhost", "127.0.0.1", "::1"}
        if parts.scheme == "http" and not (self.allow_insecure_localhost and loopback):
            raise ValueError("plain HTTP is allowed only for explicit loopback development")
        return self
