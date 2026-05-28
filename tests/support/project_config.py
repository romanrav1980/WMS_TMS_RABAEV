from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "project.defaults.json"


@dataclass(frozen=True)
class LocalProjectConfig:
    host: str
    frontend_port: int
    api_port: int
    frontend_base_url: str
    api_base_url: str
    oracle_dsn: str


def local_config() -> LocalProjectConfig:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["local"]
    host = os.getenv("TMS_LOCAL_HOST", data["loopbackHost"])
    frontend_port = int(os.getenv("TMS_FRONTEND_PORT", str(data["frontendPort"])))
    api_port = int(os.getenv("TMS_API_PORT", str(data["apiPort"])))
    return LocalProjectConfig(
        host=host,
        frontend_port=frontend_port,
        api_port=api_port,
        frontend_base_url=os.getenv("TMS_FRONTEND_BASE_URL", f"http://{host}:{frontend_port}"),
        api_base_url=os.getenv("TMS_API_BASE_URL", os.getenv("WMS_API_BASE", f"http://{host}:{api_port}")),
        oracle_dsn=os.getenv("TMS_ORACLE_DSN", os.getenv("WMS_ORACLE_DSN", data["oracleDsn"])),
    )
