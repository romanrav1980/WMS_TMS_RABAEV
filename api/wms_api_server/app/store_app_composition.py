"""Wire the standalone store reader to existing delivery and Oracle boundaries."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .oracle_gateway import OracleGateway
from .static_content import register_web_media_types
from .modules.delivery.public import (StoreAppReads,store_app_service,store_app_router,
    store_scale_requests_service,store_scale_requests_router,build_store_scale_requests)


def register_store_application(app: FastAPI) -> None:
    register_web_media_types()
    app.dependency_overrides[store_app_service] = lambda: StoreAppReads(OracleGateway())
    app.include_router(store_app_router)
    app.dependency_overrides[store_scale_requests_service] = lambda: build_store_scale_requests(OracleGateway())
    app.include_router(store_scale_requests_router)

    build = Path(__file__).resolve().parents[3] / "terminal/wms_terminal_web/dist"
    if (build / "store/index.html").is_file() and (build / "assets").is_dir():
        app.mount("/store", StaticFiles(directory=build / "store", html=True), name="store-application")
        app.mount("/assets", StaticFiles(directory=build / "assets"), name="store-application-assets")
