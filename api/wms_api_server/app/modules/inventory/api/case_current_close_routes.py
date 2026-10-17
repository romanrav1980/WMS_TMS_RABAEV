"""Identity-only close; native current authority is independent of admin-shell access."""
from typing import Any
from fastapi import APIRouter, Depends, Path
from ...platform.public import AdminUser, get_current_user
from ..contracts_case_current_close import CaseCurrentCloseInput, CaseCurrentClosePort, case_current_close_service

router = APIRouter(prefix="/api/case-pick", tags=["case-pick-current-close"])


@router.post("/tasks/{task_id}/close-current")
def close(body: CaseCurrentCloseInput, task_id: int = Path(gt=0),
          user: AdminUser = Depends(get_current_user),
          service: CaseCurrentClosePort = Depends(case_current_close_service)) -> dict[str, Any]:
    return service.close(task_id, body, user.username)
