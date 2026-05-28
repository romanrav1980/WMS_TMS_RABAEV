"""
transport_tariffs.py — Управление тарифами перевозок.

Sprint 112: просмотр и редактирование тарифной сетки.
Тарифы хранятся в таблице, которую использует Oracle-функция stoim_tt.
Модуль выполняет reverse-engineering через DESCRIBE и предоставляет
безопасный read-only + edit-через-пакеты интерфейс.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import AdminUser, BILLING_CREATE_PRICE_PERMISSION, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/transport/tariffs", tags=["transport-tariffs"])


class TariffCreateRequest(BaseModel):
    region: str = Field(..., min_length=1)
    transport_type: str = Field(..., min_length=1)
    price_per_km: float = Field(0, ge=0)
    base_price: float = Field(0, ge=0)
    price_per_pallet: float = Field(0, ge=0)
    company: str | None = None
    note: str | None = None


class TariffUpdateRequest(BaseModel):
    price_per_km: float = Field(0, ge=0)
    base_price: float = Field(0, ge=0)
    price_per_pallet: float = Field(0, ge=0)
    note: str | None = None


def _gw() -> OracleGateway:
    return OracleGateway()


def _get_tariff_table() -> str | None:
    """Определяем существующую таблицу тарифов в Oracle."""
    gw = _gw()
    candidates = ["RRL_TT_PRICE", "RRL_TRANSPORT_PRICE", "RRL_TARIFF", "RRL_TT_TARIFF"]
    for t in candidates:
        rows = gw.fetch_all(
            "SELECT COUNT(*) AS CNT FROM ALL_TABLES WHERE OWNER='RABAEV' AND TABLE_NAME=:t",
            {"t": t},
        )
        if int((rows[0] if rows else {}).get("cnt") or 0) > 0:
            return t
    return None


@router.get("")
def list_tariffs(
    region: str | None = None,
    transport_type: str | None = None,
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Список тарифов (Sprint 112). Если таблица тарифов не найдена — возвращает пустой список."""
    table = _get_tariff_table()
    if not table:
        return []
    gw = _gw()
    try:
        where_parts = []
        params: dict = {}
        if region:
            where_parts.append("REGION = :region")
            params["region"] = region
        if transport_type:
            where_parts.append("TRANSPORT_TYPE = :tt")
            params["tt"] = transport_type
        where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        rows = gw.fetch_all(
            f"SELECT * FROM RABAEV.{table} {where} ORDER BY REGION, TRANSPORT_TYPE FETCH FIRST 500 ROWS ONLY",
            params,
        )
        return [{str(k).upper(): v for k, v in r.items()} for r in rows]
    except Exception as exc:
        return [{"error": str(exc), "table": table}]


@router.get("/table-info")
def get_tariff_table_info(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Информация о таблице тарифов в Oracle (Sprint 112)."""
    table = _get_tariff_table()
    if not table:
        return {"table": None, "message": "Таблица тарифов не найдена в схеме RABAEV"}
    gw = _gw()
    cols = gw.fetch_all(
        "SELECT COLUMN_NAME, DATA_TYPE FROM ALL_TAB_COLUMNS WHERE OWNER='RABAEV' AND TABLE_NAME=:t ORDER BY COLUMN_ID",
        {"t": table},
    )
    cnt = gw.fetch_all(f"SELECT COUNT(*) AS CNT FROM RABAEV.{table}")
    return {
        "table": f"RABAEV.{table}",
        "columns": [{"name": str(c.get("column_name")), "type": str(c.get("data_type"))} for c in cols],
        "rows": int((cnt[0] if cnt else {}).get("cnt") or 0),
    }
