"""Bind the optional provenance archive without modifying any stock command."""
from fastapi import FastAPI
from .modules.integrations.public import (build_scale_evidence, scale_evidence_router,
                                          scale_evidence_service)


def register_scale_evidence(app: FastAPI) -> None:
    app.dependency_overrides[scale_evidence_service] = build_scale_evidence
    app.include_router(scale_evidence_router)
