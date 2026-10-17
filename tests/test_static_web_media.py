"""Regression for Windows .js associations making production modules unloadable."""
import mimetypes
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from api.wms_api_server.app.static_content import register_web_media_types


def test_production_modules_override_bad_registry_type_without_resetting_other_types(tmp_path: Path) -> None:
    mimetypes.add_type("text/plain", ".js")
    mimetypes.add_type("application/x-local-test", ".local-test")
    (tmp_path / "entry.js").write_text("export const ready = true;", encoding="utf-8")
    (tmp_path / "manifest.webmanifest").write_text('{"display":"standalone"}', encoding="utf-8")
    register_web_media_types()
    assert mimetypes.guess_type("test.local-test")[0] == "application/x-local-test"
    app = FastAPI()
    app.mount("/assets", StaticFiles(directory=tmp_path))
    http = TestClient(app)
    module = http.get("/assets/entry.js")
    assert module.status_code == 200 and module.headers["content-type"].startswith("text/javascript")
    assert module.text == "export const ready = true;"
    assert http.get("/assets/manifest.webmanifest").headers["content-type"].startswith("application/manifest+json")
