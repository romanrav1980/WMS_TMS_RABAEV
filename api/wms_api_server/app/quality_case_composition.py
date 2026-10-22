"""Mount TRADECASE exceptions: quarantine, quality cases and count discrepancies (C-0152)."""
from fastapi import FastAPI
from .modules.inventory.public import quality_case_router, quality_case_service, build_quality_cases


def register_quality_cases(app: FastAPI) -> None:
    app.dependency_overrides[quality_case_service] = build_quality_cases
    app.include_router(quality_case_router)
