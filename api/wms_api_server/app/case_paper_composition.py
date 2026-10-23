"""Mount the CASE pick paper sheet (BP15, C-0156) on the existing scoped CASE access and the native line signature."""
from typing import Any
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.inventory.public import CasePaperError, OracleCasePaper, case_paper_router, case_paper_service
from .modules.resources.public import CaseReadError, assert_case_task_access


def case_scope(cur: Any, task: int, actor: str, permission: str) -> None:
    try:
        assert_case_task_access(cur, task, actor, permission)
    except CaseReadError as exc:
        raise CasePaperError(exc.code, exc.status) from exc


def register_case_paper(app: FastAPI) -> None:
    app.dependency_overrides[case_paper_service] = lambda: OracleCasePaper(OracleGateway(), case_scope)
    app.include_router(case_paper_router)
