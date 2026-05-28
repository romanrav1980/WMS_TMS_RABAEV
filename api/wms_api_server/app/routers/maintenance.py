"""
maintenance.py — DB archiving + table stats.

Sprint 114: архивирование рейсов + maintenance API.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..auth import AdminUser, RIGHTS_ADMIN_EDIT_PERMISSION, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/transport/maintenance", tags=["maintenance"])


def _gw() -> OracleGateway:
    return OracleGateway()


@router.get("/stats")
def get_table_stats(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Размеры основных таблиц TMS-2 (Sprint 114)."""
    tables = [
        "RRL_TRANSPORT_TASK", "RRL_SBORKA_PALLETS",
        "RRL_TT_OPERATIONS", "RRL_VEHICLE_GPS", "RRL_BILL_ORDERS",
        "RRL_ADDR_DISTANCE_MATRIX", "RRL_PLANNER_PLANS",
    ]
    result = []
    gw = _gw()
    for t in tables:
        try:
            cnt = gw.fetch_all(
                f"SELECT COUNT(*) AS CNT FROM RABAEV.{t}"
            )
            result.append({
                "table": f"RABAEV.{t}",
                "rows": int((cnt[0] if cnt else {}).get("cnt") or 0),
            })
        except Exception as exc:
            result.append({"table": f"RABAEV.{t}", "rows": -1, "error": str(exc)})
    return result


@router.post("/archive")
def archive_old_tasks(
    older_than_months: int = Query(default=24, ge=1, le=120),
    dry_run: bool = Query(default=True, description="True=только подсчёт, False=реальное архивирование"),
    _user: AdminUser = Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION)),
) -> dict:
    """Архивировать рейсы старше N месяцев (Sprint 114).

    При dry_run=True только показывает количество без изменений.
    При dry_run=False копирует в RRL_TRANSPORT_TASK_ARCH и удаляет из основной таблицы.
    """
    gw = _gw()
    # Считаем сколько будет архивировано
    count_rows = gw.fetch_all(
        """
        SELECT COUNT(*) AS CNT
          FROM RABAEV.RRL_TRANSPORT_TASK
         WHERE SHIPMENT_DATE < ADD_MONTHS(SYSDATE, -:months)
           AND NVL(DELETED,0) = 1
        """,
        {"months": older_than_months},
    )
    count = int((count_rows[0] if count_rows else {}).get("cnt") or 0)

    if dry_run or count == 0:
        return {
            "dry_run": dry_run,
            "tasks_to_archive": count,
            "older_than_months": older_than_months,
            "archived": 0,
        }

    # Создаём архивную таблицу если нет
    try:
        gw.execute(
            "CREATE TABLE RABAEV.RRL_TRANSPORT_TASK_ARCH AS SELECT * FROM RABAEV.RRL_TRANSPORT_TASK WHERE 1=0"
        )
    except Exception:
        pass  # уже существует

    # Копируем
    gw.execute(
        """
        INSERT INTO RABAEV.RRL_TRANSPORT_TASK_ARCH
        SELECT * FROM RABAEV.RRL_TRANSPORT_TASK
         WHERE SHIPMENT_DATE < ADD_MONTHS(SYSDATE, -:months)
           AND NVL(DELETED,0) = 1
        """,
        {"months": older_than_months},
    )
    gw.execute(
        """
        DELETE FROM RABAEV.RRL_TRANSPORT_TASK
         WHERE SHIPMENT_DATE < ADD_MONTHS(SYSDATE, -:months)
           AND NVL(DELETED,0) = 1
        """,
        {"months": older_than_months},
    )

    return {
        "dry_run": False,
        "tasks_to_archive": count,
        "older_than_months": older_than_months,
        "archived": count,
    }
