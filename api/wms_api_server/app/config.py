from dataclasses import dataclass
import json
import os
from pathlib import Path


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
    slow_sql_enabled: bool
    slow_sql_threshold_ms: int
    slow_sql_max_text_chars: int
    slow_sql_max_params_chars: int
    admin_auth_enabled: bool
    production_exchange_root_dir: str


def _split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _project_local_defaults() -> dict:
    config_path = Path(__file__).resolve().parents[3] / "config" / "project.defaults.json"
    return json.loads(config_path.read_text(encoding="utf-8"))["local"]


def get_settings() -> Settings:
    local_defaults = _project_local_defaults()
    loopback_host = os.getenv("TMS_LOCAL_HOST", local_defaults["loopbackHost"])
    api_port = os.getenv("TMS_API_PORT", str(local_defaults["apiPort"]))
    return Settings(
        oracle_user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        oracle_password=os.getenv("WMS_ORACLE_PASSWORD", ""),
        oracle_dsn=os.getenv("WMS_ORACLE_DSN", local_defaults["oracleDsn"]),
        api_title=os.getenv("WMS_API_TITLE", "WMS/TMS API Server"),
        api_version=os.getenv("WMS_API_VERSION", "0.1.0"),
        cors_origins=_split_origins(os.getenv("WMS_CORS_ORIGINS", "*")),
        audit_enabled=_bool_env("WMS_API_AUDIT_ENABLED", "1"),
        audit_local_dir=os.getenv("WMS_API_AUDIT_LOCAL_DIR", "runtime/api_audit"),
        audit_max_body_chars=int(os.getenv("WMS_API_AUDIT_MAX_BODY_CHARS", "200000")),
        audit_capture_response_body=_bool_env("WMS_API_AUDIT_CAPTURE_RESPONSE_BODY", "1"),
        audit_replay_base_url=os.getenv("WMS_API_REPLAY_BASE_URL", f"http://{loopback_host}:{api_port}"),
        slow_sql_enabled=_bool_env("WMS_SQL_SLOW_LOG_ENABLED", "1"),
        slow_sql_threshold_ms=int(os.getenv("WMS_SQL_SLOW_MS", "500")),
        slow_sql_max_text_chars=int(os.getenv("WMS_SQL_SLOW_MAX_TEXT_CHARS", "4000")),
        slow_sql_max_params_chars=int(os.getenv("WMS_SQL_SLOW_MAX_PARAMS_CHARS", "4000")),
        admin_auth_enabled=_bool_env("WMS_ADMIN_AUTH_ENABLED", "1"),
        production_exchange_root_dir=os.getenv("WMS_PRODUCTION_EXCHANGE_ROOT_DIR", "exchange/production_release"),
    )
