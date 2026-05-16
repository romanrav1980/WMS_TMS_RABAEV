from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    oracle_user: str
    oracle_password: str
    oracle_dsn: str
    api_title: str
    api_version: str
    cors_origins: list[str]


def _split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def get_settings() -> Settings:
    return Settings(
        oracle_user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        oracle_password=os.getenv("WMS_ORACLE_PASSWORD", ""),
        oracle_dsn=os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
        api_title=os.getenv("WMS_API_TITLE", "WMS/TMS API Server"),
        api_version=os.getenv("WMS_API_VERSION", "0.1.0"),
        cors_origins=_split_origins(os.getenv("WMS_CORS_ORIGINS", "*")),
    )
