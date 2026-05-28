"""Shared test configuration — all ports/hosts in one place.

Override via environment variables before running tests:
    TMS_API_BASE_URL=http://myserver:8088 pytest tests/transport/
    TMS_API_USER=admin TMS_API_PASS=secret pytest tests/transport/
"""
import os

API_BASE: str = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
API_AUTH: tuple[str, str] = (
    os.environ.get("TMS_API_USER", "admin"),
    os.environ.get("TMS_API_PASS", "admin123"),
)
