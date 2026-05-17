from fastapi import APIRouter, Depends, HTTPException

from ..auth import AdminUser, SLOW_SQL_VIEW_PERMISSION, require_permission
from ..services.slow_sql_service import SlowSqlService

router = APIRouter(prefix="/api/admin/slow-sql", tags=["slow-sql"])


@router.get("")
def list_slow_sql(
    from_log_id: int | None = None,
    to_log_id: int | None = None,
    api_call_id: int | None = None,
    path_like: str | None = None,
    sql_hash: str | None = None,
    min_elapsed_ms: int | None = None,
    error_only: int | None = None,
    limit: int = 100,
    offset: int = 0,
    _user: AdminUser = Depends(require_permission(SLOW_SQL_VIEW_PERMISSION)),
) -> list[dict]:
    return SlowSqlService().list_entries(
        from_log_id=from_log_id,
        to_log_id=to_log_id,
        api_call_id=api_call_id,
        path_like=path_like,
        sql_hash=sql_hash,
        min_elapsed_ms=min_elapsed_ms,
        error_only=error_only,
        limit=limit,
        offset=offset,
    )


@router.get("/top")
def top_slow_sql(
    limit: int = 50,
    _user: AdminUser = Depends(require_permission(SLOW_SQL_VIEW_PERMISSION)),
) -> list[dict]:
    return SlowSqlService().top_entries(limit=limit)


@router.get("/oracle-top")
def oracle_top_sql(
    limit: int = 50,
    _user: AdminUser = Depends(require_permission(SLOW_SQL_VIEW_PERMISSION)),
) -> dict:
    return SlowSqlService().oracle_top_sql(limit=limit)


@router.get("/{log_id}")
def get_slow_sql(
    log_id: int,
    _user: AdminUser = Depends(require_permission(SLOW_SQL_VIEW_PERMISSION)),
) -> dict:
    entry = SlowSqlService().get_entry(log_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Slow SQL log entry not found.")
    return entry
