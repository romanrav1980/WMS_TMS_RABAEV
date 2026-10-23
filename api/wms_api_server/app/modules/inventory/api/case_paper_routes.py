"""Paper sheet of an existing CASE pick task (C-0156): READ ONLY snapshot and the version check of a scanned CPICK sheet."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_case_paper import CasePaperError, CasePaperPort, case_paper_service

router = APIRouter(prefix="/api/case-pick/tasks/{task}/paper", tags=["case-pick"])


@router.get("")
def paper(task: int = Path(gt=0), line: int | None = Query(default=None, gt=0),
          expected_signature: str | None = Query(default=None, pattern=r"^[A-F0-9]{64}$"),
          user: AdminUser = Depends(get_current_user), service: CasePaperPort = Depends(case_paper_service)) -> dict[str, Any]:
    try:
        return service.snapshot(task, user.username, line, expected_signature)
    except CasePaperError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc
