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
    audit_enabled: bool
    audit_local_dir: str
    audit_max_body_chars: int
    audit_capture_response_body: bool
    audit_replay_base_url: str
    admin_auth_enabled: bool


def _split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        oracle_user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        oracle_password=os.getenv("WMS_ORACLE_PASSWORD", ""),
        oracle_dsn=os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
        api_title=os.getenv("WMS_API_TITLE", "WMS/TMS API Server"),
        api_version=os.getenv("WMS_API_VERSION", "0.1.0"),
        cors_origins=_split_origins(os.getenv("WMS_CORS_ORIGINS", "*")),
        audit_enabled=_bool_env("WMS_API_AUDIT_ENABLED", "1"),
        audit_local_dir=os.getenv("WMS_API_AUDIT_LOCAL_DIR", "runtime/api_audit"),
        audit_max_body_chars=int(os.getenv("WMS_API_AUDIT_MAX_BODY_CHARS", "200000")),
        audit_capture_response_body=_bool_env("WMS_API_AUDIT_CAPTURE_RESPONSE_BODY", "1"),
        audit_replay_base_url=os.getenv("WMS_API_REPLAY_BASE_URL", "http://127.0.0.1:8088"),
        admin_auth_enabled=_bool_env("WMS_ADMIN_AUTH_ENABLED", "1"),
    )
