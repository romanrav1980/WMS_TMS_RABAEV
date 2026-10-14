"""
transport_service.py — Сервис диспетчера отгрузки.

Фаза 1 (ручное назначение) + улучшения 2026-05-22:
  — Фильтры списка СТ: addr_mask, st_mask, ware_ids, assembled_only,
    max_weight_kg, max_volume_m3
  — Новые поля в get_task_sts(): TIME_FROM, TIME_TO, ZONE, LOAD_TYPE
  — Новые поля в list_tasks(): TK_NAME, IS_OWN_DRIVER, READY_PERC, UNREADY_COUNT
  — Проверка минимальной загрузки (TRANSPORT_TASK.can_print) перед закрытием
  — Вызов RRL_TT_SET_TRANSCOMMENT при смене машины
  — set_st_load_type() — изменить способ погрузки СТ (Г/П)
  — set_st_order()     — изменить порядок адреса (ORD) в рейсе

Фаза 2.1 (кластеры):
  — list_clusters()            — группировка свободных СТ по RRL_ADDR.RAION
  — create_task_from_cluster() — создать рейс из всех СТ района (Sprint 29)

Sprint 8 (VRP):
  — solve_vrp()        — запуск OR-Tools/Clarke-Wright, сохранение плана
  — apply_vrp_plan()   — создать рейсы из плана через Oracle-пакеты
  — get_plan_metrics() — агрегированные метрики плана

Все мутации данных выполняются через существующие Oracle-функции:
  RRL_TRASPORT_TASK_ADD  — создать рейс
  RRL_TT_ADD_PALL        — назначить / снять СТ (tt_id=0 → снять)
  RRL_TT_REORDER_ADR     — пересортировать СТ в рейсе по ORD адреса
"""

import json
import time
import threading
from datetime import date, datetime, time as dt_time, timedelta
from typing import Any, Callable

from fastapi import HTTPException

from ..modules.transport.public import normalize_transport_type as _normalize_transtype, available_sts_query
from ..db import rows_as_dicts
from ..oracle_gateway import OracleGateway
from ..schemas import (
    OperationFactUpdate,
    TransportTaskCreateRequest,
    TransportTaskUpdateRequest,
    VrpPlanResponse,
    VrpRouteItem,
    VrpRouteStop,
)


def _upper_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).upper(): value for key, value in row.items()}


_AVAILABLE_STS_CACHE_TTL_SEC = 15.0
_AVAILABLE_STS_CACHE: dict[tuple[Any, ...], tuple[float, list[dict[str, Any]]]] = {}
_AVAILABLE_STS_CACHE_LOCK = threading.Lock()
_TASK_STS_CACHE_TTL_SEC = 3.0
_TASK_STS_CACHE: dict[int, tuple[float, list[dict[str, Any]]]] = {}
_TASK_STS_CACHE_LOCK = threading.Lock()
_REF_CACHE_TTL_SEC = 60.0
_REF_CACHE: dict[tuple[str, Any], tuple[float, list[dict[str, Any]]]] = {}
_REF_CACHE_LOCK = threading.Lock()
_VEHICLE_AVAILABILITY_CACHE_TTL_SEC = 5.0
_VEHICLE_AVAILABILITY_CACHE: dict[tuple[str, int], tuple[float, list[dict[str, Any]]]] = {}
_VEHICLE_AVAILABILITY_CACHE_LOCK = threading.Lock()


def _clear_available_sts_cache() -> None:
    with _AVAILABLE_STS_CACHE_LOCK:
        _AVAILABLE_STS_CACHE.clear()
    _invalidate_ref_cache("planner_orders")


def _clear_task_sts_cache(task_id: int | None = None) -> None:
    with _TASK_STS_CACHE_LOCK:
        if task_id is None:
            _TASK_STS_CACHE.clear()
        else:
            _TASK_STS_CACHE.pop(task_id, None)


def _clear_vehicle_availability_cache() -> None:
    with _VEHICLE_AVAILABILITY_CACHE_LOCK:
        _VEHICLE_AVAILABILITY_CACHE.clear()


def _invalidate_ref_cache(prefix: str) -> None:
    """Инвалидировать записи _REF_CACHE с ключами, начинающимися на prefix."""
    with _REF_CACHE_LOCK:
        stale = [k for k in list(_REF_CACHE.keys()) if k[0] == prefix]
        for k in stale:
            _REF_CACHE.pop(k, None)


def _minutes_from_shift_start(value: Any, shift_start_hour: int = 6, default: int | None = None) -> int | None:
    """Convert Oracle date/time/string values to minutes from the dispatch shift start."""
    if value is None:
        return default
    try:
        if isinstance(value, datetime):
            total = value.hour * 60 + value.minute
        elif isinstance(value, dt_time):
            total = value.hour * 60 + value.minute
        else:
            text = str(value).strip()
            if not text:
                return default
            if "T" in text:
                parsed = datetime.fromisoformat(text.replace("Z", ""))
                total = parsed.hour * 60 + parsed.minute
            elif " " in text and ":" in text:
                parsed = datetime.strptime(text[:16], "%Y-%m-%d %H:%M")
                total = parsed.hour * 60 + parsed.minute
            elif ":" in text:
                hh, mm = text[:5].split(":")
                total = int(hh) * 60 + int(mm)
            else:
                return default
    except Exception:
        return default
    return max(0, total - shift_start_hour * 60)


def _fallback_time_window_from_ord(ord_value: Any) -> tuple[int, int]:
    """Fallback store acceptance window when legacy ST rows do not carry one."""
    try:
        ord_int = max(1, int(ord_value or 1))
    except Exception:
        ord_int = 1
    slot = (ord_int - 1) % 4
    start = 60 + slot * 180  # 07:00, 10:00, 13:00, 16:00 from a 06:00 shift start
    return start, start + 240


def _clock_from_shift_minutes(minutes_from_shift: int, shift_start_hour: int = 6) -> str:
    """Return HH:MM clock string from minutes after the dispatch shift start."""
    total = (shift_start_hour * 60 + int(minutes_from_shift)) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def _fill_visible_time_window(row: dict[str, Any]) -> dict[str, Any]:
    """Expose the same fallback TW used by VRP on read endpoints for traceability."""
    if row.get("TIME_FROM") is None or row.get("TIME_TO") is None:
        fallback_from, fallback_to = _fallback_time_window_from_ord(row.get("ORD"))
        if row.get("TIME_FROM") is None:
            row["TIME_FROM"] = _clock_from_shift_minutes(fallback_from)
        if row.get("TIME_TO") is None:
            row["TIME_TO"] = _clock_from_shift_minutes(fallback_to)
    if not row.get("ZONE"):
        row["ZONE"] = row.get("RAION") or row.get("REGION") or row.get("ADDR")
    return row


def _normalize_task_condition(value: Any) -> Any:
    """Legacy package-created open tasks can store Cyrillic as question marks."""
    if isinstance(value, str) and value and set(value.strip()) == {"?"}:
        return "Открыт"
    return value


def _normalize_task_row(row: dict[str, Any]) -> dict[str, Any]:
    if "CONDITION" in row:
        row["CONDITION"] = _normalize_task_condition(row.get("CONDITION"))
    if "STATUS" in row:
        row["STATUS"] = _normalize_task_condition(row.get("STATUS"))
    return row


def _cached_ref(key: tuple[str, Any], loader: Callable[[], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    now = time.monotonic()
    with _REF_CACHE_LOCK:
        cached = _REF_CACHE.get(key)
        if cached and now - cached[0] <= _REF_CACHE_TTL_SEC:
            return [dict(row) for row in cached[1]]
    rows = loader()
    with _REF_CACHE_LOCK:
        _REF_CACHE[key] = (time.monotonic(), [dict(row) for row in rows])
    return rows


class _TransportGateway:
    """Transport API keeps legacy Oracle-style uppercase response keys."""

    def __init__(self, gateway: OracleGateway) -> None:
        self._gateway = gateway

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return [_upper_keys(row) for row in self._gateway.fetch_all(sql, params)]

    def __getattr__(self, name: str) -> Any:
        return getattr(self._gateway, name)


class TransportService:
    def __init__(self, gateway: OracleGateway | None = None, departure: Callable[[int, str], dict[str, Any]] | None = None) -> None:
        self.gateway = _TransportGateway(gateway or OracleGateway())
        self._departure = departure

    # ------------------------------------------------------------------
    # Справочники
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Кластеры свободных СТ (Phase 2.1)
    # ------------------------------------------------------------------

    def list_clusters(
        self,
        stdate: date | None = None,
        ware_ids: list[int] | None = None,
    ) -> list[dict[str, Any]]:
        """Группирует свободные СТ по RAION. Вычисляется в Python поверх list_available_sts."""
        sts = self.list_available_sts(stdate=stdate, unassigned_only=True, ware_ids=ware_ids)
        clusters: dict[str, dict[str, Any]] = {}
        for st in sts:
            raion: str = st.get("RAION") or "(без района)"
            if raion not in clusters:
                clusters[raion] = {
                    "RAION": raion,
                    "ST_COUNT": 0,
                    "PALLET_COUNT": 0,
                    "WEIGHT_KG": 0.0,
                    "VOLUME_M3": 0.0,
                    "STS": [],
                }
            c = clusters[raion]
            c["ST_COUNT"] += 1
            c["PALLET_COUNT"] += st.get("PALLETS_COUNT") or 0
            c["WEIGHT_KG"] = round(c["WEIGHT_KG"] + (st.get("WEIGHT_KG") or 0), 0)
            c["VOLUME_M3"] = round(c["VOLUME_M3"] + (st.get("VOLUME_M3") or 0), 2)
            c["STS"].append(st)
        # Районы с именами — по алфавиту; «без района» — в конец
        return sorted(
            clusters.values(),
            key=lambda x: (x["RAION"] == "(без района)", x["RAION"]),
        )

    def create_task_from_cluster(
        self,
        raion: str,
        req: "ClusterCreateTaskRequest",
        user_id: str,
    ) -> dict[str, Any]:
        """Создаёт рейс из всех свободных СТ района одним запросом (Sprint 29, Phase 2).

        Существующий поиск СТ района; создание, реквизиты и назначение
        исполняются в одной транзакции с общим native capacity validator.
        """
        # 1. Собрать свободные СТ района — server-side raion filter (Sprint 35)
        sts = self.list_available_sts(
            stdate=req.stdate,
            unassigned_only=True,
            ware_ids=req.ware_ids,
            raion=raion,
        )
        from ..modules.transport.public import create_existing_cluster, TransportPlanError
        fields={key:value for key,value in {
            "transport":req.vehicle,"voditel_id":req.driver_id,"dock":req.dock,
        }.items() if value is not None}
        try:
            return create_existing_cluster(self.gateway,raion,req.stdate,
                _normalize_transtype(req.transtype),fields,
                [str(row["ST_NUMBER"]) for row in sts],user_id,req.operation_id,req.ware_ids)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc

    def list_vehicles(self, active_only: bool = True) -> list[dict[str, Any]]:
        def load() -> list[dict[str, Any]]:
            where = "WHERE NVL(BLOCKED,0)=0 AND NVL(DELETED,0)=0" if active_only else ""
            return self.gateway.fetch_all(
                f"""
                SELECT ID, NUM, TR_TYPE, MARKA, REF_REJIM,
                       PALLETS, GIDROBORT, BLOCKED, MAX_WEIGHT_KG, DELETED
                  FROM RABAEV.RRL_TR_VEHICLE
                  {where}
                 ORDER BY TR_TYPE, NUM
                """
            )

        return _cached_ref(("vehicles", active_only), load)

    # ------------------------------------------------------------------
    # Sprint 97 — Fleet CRUD: Vehicles
    # ------------------------------------------------------------------

    def list_vehicles_full(self) -> list[dict[str, Any]]:
        """Все ТС для страницы управления флотом (Sprint 97)."""
        rows = self.gateway.fetch_all(
            """
            SELECT V.ID,
                   V.NUM          AS NUM_PLAT,
                   V.TR_TYPE      AS TRANSTYPE_ID,
                   V.TR_TYPE      AS TRANSTYPE_NAME,
                   NVL(V.MAX_WEIGHT_KG, 10000) AS MAX_WEIGHT_KG,
                   NVL(V.PALLETS, 20)           AS MAX_PALLETS,
                   NVL(V.SOBSTVENNYY, 1)        AS SOBSTVENNYY,
                   V.DOVERENNOST_OT,
                   NVL(V.BLOCKED, 0)            AS BLOCKED
              FROM RABAEV.RRL_TR_VEHICLE V
             WHERE NVL(V.DELETED, 0) = 0
             ORDER BY V.ID
            """
        )
        return [_upper_keys(r) for r in rows]

    def create_vehicle(
        self,
        num_plat: str,
        transtype_id: str | None,
        max_weight_kg: int,
        max_pallets: int,
        sobstvennyy: bool,
        doverennost_ot: str | None,
    ) -> int:
        # RRL_TR_VEHICLE_ADD uses actual column names (NUM, TR_TYPE) after 055_fix.sql
        new_id = self.gateway.call_number_plsql(
            """
            BEGIN
              :result := RABAEV.RRL_TR_VEHICLE_ADD(
                :num_plat, :transtype_id, :max_weight_kg,
                :max_pallets, :sobstvennyy, :doverennost_ot
              );
            END;
            """,
            {
                "num_plat": num_plat,
                "transtype_id": transtype_id,
                "max_weight_kg": max_weight_kg,
                "max_pallets": max_pallets,
                "sobstvennyy": 1 if sobstvennyy else 0,
                "doverennost_ot": doverennost_ot,
            },
        )
        _invalidate_ref_cache("vehicles")
        return new_id

    def update_vehicle(
        self,
        vehicle_id: int,
        num_plat: str,
        transtype_id: str | None,
        max_weight_kg: int,
        max_pallets: int,
        sobstvennyy: bool,
        doverennost_ot: str | None,
    ) -> None:
        self.gateway.execute(
            """
            BEGIN
              RABAEV.RRL_TR_VEHICLE_UPDATE(
                :vid, :num_plat, :transtype_id, :max_weight_kg,
                :max_pallets, :sobstvennyy, :doverennost_ot
              );
            END;
            """,
            {
                "vid": vehicle_id,
                "num_plat": num_plat,
                "transtype_id": transtype_id,
                "max_weight_kg": max_weight_kg,
                "max_pallets": max_pallets,
                "sobstvennyy": 1 if sobstvennyy else 0,
                "doverennost_ot": doverennost_ot,
            },
        )
        _invalidate_ref_cache("vehicles")

    def delete_vehicle(self, vehicle_id: int) -> None:
        self.gateway.execute(
            "BEGIN RABAEV.RRL_TR_VEHICLE_DEL(:vid); END;",
            {"vid": vehicle_id},
        )
        _invalidate_ref_cache("vehicles")

    def list_drivers(self, active_only: bool = True) -> list[dict[str, Any]]:
        def load() -> list[dict[str, Any]]:
            where = "WHERE (DELETED IS NULL OR DELETED = 0)" if active_only else ""
            return self.gateway.fetch_all(
                f"""
                SELECT ID,
                       TRIM(F || ' ' || I || ' ' || O) AS FULL_NAME,
                       F, I, O, TEL, TRANSPORT_NUM,
                       SOBSTVENNYY, DOVERENNOST_OT
                  FROM RABAEV.RRL_TR_VODITEL
                  {where}
                 ORDER BY F, I
                """
            )

        return _cached_ref(("drivers", active_only), load)

    # ------------------------------------------------------------------
    # Sprint 98 — Fleet CRUD: Drivers
    # ------------------------------------------------------------------

    def list_drivers_full(self) -> list[dict[str, Any]]:
        """Все водители для страницы управления флотом."""
        rows = self.gateway.fetch_all(
            """
            SELECT ID,
                   TRIM(NVL(F,'') || ' ' || NVL(I,'') || ' ' || NVL(O,'')) AS FULL_NAME,
                   TEL            AS PHONE,
                   LICENSE_NUMBER,
                   COMPANY,
                   SOBSTVENNYY,
                   DOVERENNOST_OT
              FROM RABAEV.RRL_TR_VODITEL
             WHERE NVL(DELETED, 0) = 0
             ORDER BY F, I
            """
        )
        return [_upper_keys(r) for r in rows]

    def create_driver(
        self,
        name: str,
        phone: str | None,
        license_number: str | None,
        company: str | None,
    ) -> int:
        new_id = self.gateway.call_number_plsql(
            """
            BEGIN
              :result := RABAEV.RRL_TR_VODITEL_ADD(:name, :phone, :license_number, :company);
            END;
            """,
            {"name": name, "phone": phone, "license_number": license_number, "company": company},
        )
        _invalidate_ref_cache("drivers")
        return new_id

    def update_driver(
        self,
        driver_id: int,
        name: str,
        phone: str | None,
        license_number: str | None,
        company: str | None,
    ) -> None:
        self.gateway.execute(
            """
            BEGIN
              RABAEV.RRL_TR_VODITEL_UPDATE(:did, :name, :phone, :license_number, :company);
            END;
            """,
            {"did": driver_id, "name": name, "phone": phone,
             "license_number": license_number, "company": company},
        )
        _invalidate_ref_cache("drivers")

    def delete_driver(self, driver_id: int) -> None:
        self.gateway.execute(
            "BEGIN RABAEV.RRL_TR_VODITEL_DEL(:did); END;",
            {"did": driver_id},
        )
        _invalidate_ref_cache("drivers")

    def list_transport_types(self) -> list[dict[str, Any]]:
        def load() -> list[dict[str, Any]]:
            return self.gateway.fetch_all(
                """
                SELECT TRANSPORTTYPE,
                       TRANSPORTTYPE AS NAME,
                       NORMA_PALLET  AS MIN_PALLET_LOAD,
                       NORMA_PALLET  AS MAX_PALLET_LOAD,
                       NORMA_WEIGHT,
                       REF,
                       ORD
                  FROM RABAEV.RRL_TRANSPORT_TYPE
                 ORDER BY ORD NULLS LAST, TRANSPORTTYPE
                """
            )

        return _cached_ref(("transport_types", True), load)

    # ------------------------------------------------------------------
    # Рейсы (transport tasks)
    # ------------------------------------------------------------------

    def list_tasks(
        self,
        shipment_date: date | None = None,
        condition: str | None = None,
        include_deleted: bool = False,
        include_readiness: bool = False,
        task_id: int | None = None,
        transport_mask: str | None = None,
        company_mask: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        no_payments_only: bool = False,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if not include_deleted:
            conditions.append("(TT.DELETED IS NULL OR TT.DELETED = 0)")
        if shipment_date is not None:
            conditions.append("TT.SHIPMENT_DATE >= :shipment_date AND TT.SHIPMENT_DATE < :shipment_date_next")
            params["shipment_date"] = shipment_date
            params["shipment_date_next"] = shipment_date + timedelta(days=1)
        else:
            if date_from is None and date_to is None:
                date_to = date.today()
                date_from = date_to - timedelta(days=31)
            if date_from is not None:
                conditions.append("TT.SHIPMENT_DATE >= :date_from")
                params["date_from"] = date_from
        if date_to is not None:
            conditions.append("TT.SHIPMENT_DATE < :date_to_next")
            params["date_to_next"] = date_to + timedelta(days=1)
        if condition:
            conditions.append("TT.CONDITION = :condition")
            params["condition"] = condition
        if task_id is not None:
            conditions.append("TT.ID = :task_id_f")
            params["task_id_f"] = task_id
        if transport_mask:
            conditions.append("UPPER(TT.TRANSPORT) LIKE UPPER(:transport_mask)")
            params["transport_mask"] = f"%{transport_mask}%"
        if company_mask:
            conditions.append("UPPER(NVL(V.DOVERENNOST_OT,'')) LIKE UPPER(:company_mask)")
            params["company_mask"] = f"%{company_mask}%"
        if no_payments_only:
            conditions.append("(TT.PAY_ORDER_ID IS NULL OR TT.PAY_ORDER_ID = 0)")

        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""

        readiness_cols = ""
        if include_readiness:
            readiness_cols = """,
                   ROUND(
                     COUNT(DISTINCT CASE
                       WHEN NVL(SP.PROOVED,0) = 1 OR NVL(SP.PROOVED_BY_SCAN,0) = 1
                       THEN SP.ID
                     END) * 100 / NULLIF(COUNT(DISTINCT SP.ID), 0),
                     0
                   ) AS READY_PERC,
                   COUNT(DISTINCT CASE
                     WHEN NVL(SP.PROOVED,0) <> 1 AND NVL(SP.PROOVED_BY_SCAN,0) <> 1
                     THEN SP.ID
                   END) AS UNREADY_COUNT"""

        rows = self.gateway.fetch_all(
            f"""
            SELECT TT.ID,
                   TT.CREATEDATE,
                   TT.TRANSPORT,
                   TT.TRANSTYPE,
                   TT.CONDITION,
                   TT.SHIPMENT_DATE,
                   TT.PLANNED_DELIVERY_DATE,
                   TT.VODITEL_ID,
                   TRIM(V.F || ' ' || V.I || ' ' || V.O) AS VODITEL_NAME,
                   V.TEL                                  AS VODITEL_TEL,
                   V.DOVERENNOST_OT                       AS TK_NAME,
                   V.SOBSTVENNYY                          AS IS_OWN_DRIVER,
                   TT.PRIMECHANIE,
                   TT.DOCK,
                   TT.SHIPMENT_TIME,
                   TT.TEMP_REGION,
                   TT.TEMP_REGION                         AS REGIONS,
                   TT.TEMP_WEIGHT,
                   TT.PRICE,
                   TT.DELETED,
                   TT.USER_ID                             AS LOGIST,
                   TT.PAY_ORDER_ID,
                   COUNT(DISTINCT SP.PALLET_UID)          AS PALLET_COUNT,
                   COUNT(DISTINCT SP.ST_NUMBER)           AS ST_COUNT,
                   ROUND(SUM(NVL(R.TARESIZE,0) * NVL(R.PACK_COUNT,0)) / 1000000, 2) AS VOLUME_M3
                   {readiness_cols}
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TR_VODITEL V ON V.ID = TT.VODITEL_ID
              LEFT JOIN RABAEV.RRL_SBORKA_PALLETS SP
                ON SP.TRANSTASK_ID = TT.ID
               AND SP.CONDITION <> 2
              LEFT JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = SP.PALLET_UID
              {where_sql}
             GROUP BY TT.ID, TT.CREATEDATE, TT.TRANSPORT, TT.TRANSTYPE,
                      TT.CONDITION, TT.SHIPMENT_DATE, TT.PLANNED_DELIVERY_DATE,
                      TT.VODITEL_ID, V.F, V.I, V.O, V.TEL,
                      V.DOVERENNOST_OT, V.SOBSTVENNYY,
                      TT.PRIMECHANIE, TT.DOCK, TT.SHIPMENT_TIME,
                      TT.TEMP_REGION, TT.TEMP_WEIGHT, TT.PRICE, TT.DELETED,
                      TT.USER_ID, TT.PAY_ORDER_ID
             ORDER BY TT.SHIPMENT_DATE DESC, TT.ID DESC
            """,
            params,
        )
        return [_normalize_task_row(dict(row)) for row in rows]

    def get_task(self, task_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            SELECT TT.ID,
                   TT.CREATEDATE,
                   TT.TRANSPORT,
                   TT.TRANSTYPE,
                   TT.CONDITION,
                   TT.SHIPMENT_DATE,
                   TT.PLANNED_DELIVERY_DATE,
                   TT.VODITEL_ID,
                   TRIM(V.F || ' ' || V.I || ' ' || V.O) AS VODITEL_NAME,
                   V.TEL                                  AS VODITEL_TEL,
                   V.DOVERENNOST_OT                       AS TK_NAME,
                   V.SOBSTVENNYY                          AS IS_OWN_DRIVER,
                   TT.PRIMECHANIE,
                   TT.DOCK,
                   TT.SHIPMENT_TIME,
                   TT.TEMP_REGION,
                   TT.TEMP_WEIGHT,
                   TT.PRICE,
                   TT.DELETED,
                   TT.PAY_ORDER_ID
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TR_VODITEL V ON V.ID = TT.VODITEL_ID
             WHERE TT.ID = :task_id
            """,
            {"task_id": task_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"Transport task {task_id} not found")
        return _normalize_task_row(dict(rows[0]))

    def create_task(self, req: TransportTaskCreateRequest, user_id: str) -> int:
        from ..modules.transport.public import create_existing_trip,TransportPlanError
        try:return create_existing_trip(self.gateway,_normalize_transtype(req.transtype),req.shipment_date,user_id)
        except TransportPlanError as exc:raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc

    def update_task(self, task_id: int, req: TransportTaskUpdateRequest, user_id: str) -> None:
        from ..modules.transport.public import update_existing_trip,TransportPlanError
        fields=req.model_dump(exclude_none=True,mode="json")
        if "transtype"in fields:fields["transtype"]=_normalize_transtype(fields["transtype"])
        if not fields:return
        try:update_existing_trip(self.gateway,task_id,fields,user_id)
        except TransportPlanError as exc:raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc

    def close_task(self, task_id: int, user_id: str) -> None:
        """Existing close action delegates the physical departure gate."""
        from ..modules.transport.public import TransportLoadingError
        if self._departure is None:
            raise HTTPException(503,detail={"code":"PHYSICAL_DEPARTURE_NOT_WIRED"})
        try:
            self._departure(task_id,user_id)
        except TransportLoadingError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc),
                "operation_id":exc.operation_id}) from exc
        _clear_vehicle_availability_cache()
        _clear_task_sts_cache(task_id)

    def cancel_task(self, task_id: int, user_id: str) -> None:
        from ..modules.transport.public import cancel_trip
        try:
            cancel_trip(self.gateway,task_id,user_id)
        except ValueError as exc:
            raise HTTPException(409,detail=str(exc)) from exc
        _clear_available_sts_cache()
        _clear_task_sts_cache(task_id)

    # ------------------------------------------------------------------
    # Состав рейса — СТ
    # ------------------------------------------------------------------

    def get_task_sts(self, task_id: int) -> list[dict[str, Any]]:
        now = time.monotonic()
        with _TASK_STS_CACHE_LOCK:
            cached = _TASK_STS_CACHE.get(task_id)
            if cached and now - cached[0] <= _TASK_STS_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]

        rows = self.gateway.fetch_all(
            """
            SELECT SP.ST_NUMBER,
                   SP.ADDR,
                   NVL(A.REGION, SP.ADDR)                        AS REGION,
                   A.RAION,
                   SP.ORD,
                   COUNT(DISTINCT SP.PALLET_UID)                  AS PALLETS_COUNT,
                   ROUND(SUM(NVL(R.ORDER_WEIGHT,0)),0)            AS WEIGHT_KG,
                   MAX(SP.STDATE)                                 AS STDATE,
                   MAX(SP.ZONE)                                   AS ZONE,
                   MAX(SP.ZONE_TIME_PLAN_IN)                      AS TIME_FROM,
                   MAX(SP.ZONE_TIME_PLAN_OUT)                     AS TIME_TO,
                   MAX(SP.LOAD_TYPE)                              AS LOAD_TYPE,
                   MAX(SP.WARE_ID)                                AS WARE_ID,
                   ROUND(
                     COUNT(DISTINCT CASE
                       WHEN NVL(SP.PROOVED,0) = 1 OR NVL(SP.PROOVED_BY_SCAN,0) = 1
                       THEN SP.ID
                     END) * 100 / NULLIF(COUNT(DISTINCT SP.ID), 0),
                     0
                   )                                               AS VERIFY_PERC
              FROM RABAEV.RRL_SBORKA_PALLETS SP
              JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = SP.PALLET_UID
              LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
             WHERE SP.TRANSTASK_ID = :task_id
               AND (SP.CONDITION <> 2 OR EXISTS(select 1 from RRL_TT_HU_LOAD_ST ls
                   join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
                  where ls.SBORKA_PALLET_ID=SP.ID and ls.ACTIVE_FLAG=1 and lf.TT_ID=SP.TRANSTASK_ID))
             GROUP BY SP.ST_NUMBER, SP.ADDR, A.REGION, A.RAION, SP.ORD
             ORDER BY SP.ORD NULLS LAST, SP.ST_NUMBER
            """,
            {"task_id": task_id},
        )
        with _TASK_STS_CACHE_LOCK:
            _TASK_STS_CACHE[task_id] = (time.monotonic(), [dict(row) for row in rows])
        return rows

    def assign_sts(self, task_id: int, st_numbers: list[str], user_id: str) -> dict[str, Any]:
        from ..modules.transport.public import assign_sts,TransportPlanError
        try:
            result = assign_sts(self.gateway, task_id, st_numbers,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        _clear_available_sts_cache()
        _clear_task_sts_cache(task_id)
        return result

    def unassign_st(self, task_id: int, st_number: str, user_id: str) -> None:
        from ..modules.transport.public import unassign_st
        try:
            unassign_st(self.gateway, task_id, st_number)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        _clear_available_sts_cache()
        _clear_task_sts_cache(task_id)

    def set_st_load_type(
        self, task_id: int, st_number: str, load_type: str, user_id: str
    ) -> None:
        """Установить способ погрузки СТ: '' | 'Г' | 'П'."""
        self.gateway.execute(
            """
            UPDATE RABAEV.RRL_SBORKA_PALLETS
               SET LOAD_TYPE = :load_type
             WHERE ST_NUMBER   = :st_number
               AND TRANSTASK_ID = :task_id
               AND CONDITION <> 2
            """,
            {"load_type": load_type or None, "st_number": st_number, "task_id": task_id},
        )
        _clear_task_sts_cache(task_id)

    def set_st_order(
        self, task_id: int, st_number: str, ord_value: int, user_id: str
    ) -> None:
        """Вручную задать порядок (ORD) адреса доставки в рейсе."""
        self.gateway.execute(
            """
            UPDATE RABAEV.RRL_SBORKA_PALLETS
               SET ORD = :ord_value
             WHERE ST_NUMBER   = :st_number
               AND TRANSTASK_ID = :task_id
               AND CONDITION <> 2
            """,
            {"ord_value": ord_value, "st_number": st_number, "task_id": task_id},
        )
        _clear_task_sts_cache(task_id)

    # ------------------------------------------------------------------
    # Свободные СТ
    # ------------------------------------------------------------------

    def list_available_sts(
        self,
        stdate: date | None = None,
        date_to: date | None = None,
        unassigned_only: bool = True,
        ware_id: int | None = None,
        ware_ids: list[int] | None = None,
        addr_mask: str | None = None,
        st_mask: str | None = None,
        st_mask_exclude: bool = False,
        transport_type: str | None = None,
        assembled_only: bool = False,
        not_assembled_only: bool = False,
        max_weight_kg: float | None = None,
        max_volume_m3: float | None = None,
        articul: str | None = None,
        raion: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[dict[str, Any]]:
        filters = dict(
            stdate=stdate,
            date_to=date_to,
            unassigned_only=unassigned_only,
            ware_id=ware_id,
            ware_ids=ware_ids,
            addr_mask=addr_mask,
            st_mask=st_mask,
            st_mask_exclude=st_mask_exclude,
            transport_type=transport_type,
            assembled_only=assembled_only,
            not_assembled_only=not_assembled_only,
            max_weight_kg=max_weight_kg,
            max_volume_m3=max_volume_m3,
            articul=articul,
            raion=raion,
        )
        cache_key = tuple(tuple(v) if isinstance(v,list) else v for v in filters.values())+(page,page_size)
        with _AVAILABLE_STS_CACHE_LOCK:
            cached = _AVAILABLE_STS_CACHE.get(cache_key)
            if cached and time.monotonic()-cached[0] <= _AVAILABLE_STS_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]
            sql, params = available_sts_query(**filters,page=page,page_size=page_size)
            rows=self.gateway.fetch_all(sql,params)
            for row in rows:
                row.pop("PAGE_ROW_NUMBER",None)
            normalized=[_fill_visible_time_window(dict(row)) for row in rows]
            _AVAILABLE_STS_CACHE[cache_key]=(time.monotonic(),[dict(row) for row in normalized])
            return normalized

    def _has_sborka_rows_for_period(
        self,
        stdate: date | None,
        date_to: date | None,
        unassigned_only: bool,
    ) -> bool:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if unassigned_only:
            conditions.append("TRANSTASK_ID IS NULL")
        if stdate is not None and date_to is None:
            conditions.append("STDATE >= :stdate AND STDATE < :stdate_next")
            params["stdate"] = stdate
            params["stdate_next"] = stdate + timedelta(days=1)
        elif stdate is not None and date_to is not None:
            conditions.append("STDATE >= :stdate AND STDATE < :date_to_next")
            params["stdate"] = stdate
            params["date_to_next"] = date_to + timedelta(days=1)
        elif date_to is not None:
            conditions.append("STDATE < :date_to_next")
            params["date_to_next"] = date_to + timedelta(days=1)
        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""
        rows = self.gateway.fetch_all(
            f"""
            SELECT 1 AS HAS_ROWS
              FROM RABAEV.RRL_SBORKA_PALLETS
              {where_sql}
               AND ROWNUM = 1
            """,
            params,
        )
        return bool(rows)

    # ------------------------------------------------------------------
    # Планировщик / карта заказов (Sprint 7)
    # ------------------------------------------------------------------

    def get_planner_orders(
        self,
        plan_date: date | None = None,
        ware_ids: list[int] | None = None,
        transport_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Возвращает свободные СТ с координатами для отображения на карте."""
        cache_key = (
            "planner_orders",
            plan_date,
            tuple(ware_ids or ()),
            transport_type,
        )
        now = time.monotonic()
        with _REF_CACHE_LOCK:
            cached = _REF_CACHE.get(cache_key)
            if cached and now - cached[0] <= _REF_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]

        conditions: list[str] = ["P.TRANSTASK_ID IS NULL", "P.CONDITION <> 2"]
        params: dict[str, Any] = {}

        if plan_date is not None:
            conditions.append("P.STDATE >= :plan_date AND P.STDATE < :plan_date_next")
            params["plan_date"] = plan_date
            params["plan_date_next"] = plan_date + timedelta(days=1)
            if not self._has_sborka_rows_for_period(
                stdate=plan_date,
                date_to=None,
                unassigned_only=True,
            ):
                return []

        effective_ware_ids = ware_ids or []
        if effective_ware_ids:
            placeholders = ", ".join(f":wid{i}" for i in range(len(effective_ware_ids)))
            conditions.append(f"P.WARE_ID IN ({placeholders})")
            for i, wid in enumerate(effective_ware_ids):
                params[f"wid{i}"] = wid

        if transport_type:
            conditions.append("NVL(A.TRANSPORT_TYPE, '0') = :transport_type")
            params["transport_type"] = transport_type

        where_sql = "WHERE " + " AND ".join(conditions)

        with _REF_CACHE_LOCK:
            cached = _REF_CACHE.get(cache_key)
            if cached and time.monotonic() - cached[0] <= _REF_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]
            rows = self.gateway.fetch_all(
                f"""
                SELECT P.ST_NUMBER,
                       P.ADDR,
                       NVL(A.REGION, P.ADDR) AS REGION,
                       A.RAION,
                       A.ORD,
                       MAX(P.ZONE) AS ZONE,
                       A.SHIROTA AS LAT,
                       A.DOLGOTA AS LON,
                       COUNT(DISTINCT P.PALLET_UID) AS PALLETS_COUNT,
                       ROUND(SUM(NVL(R.ORDER_WEIGHT, 0)), 0) AS WEIGHT_KG,
                       ROUND(SUM(NVL(R.TARESIZE, 0) * NVL(R.PACK_COUNT, 0)) / 1000000, 2) AS VOLUME_M3,
                       P.WARE_ID,
                       NVL(A.TRANSPORT_TYPE, '0') AS TRANSPORT_TYPE,
                       NVL(A.STOL, 0) AS NEEDS_HYDRO_BOARD,
                       A.MAX_VEHICLE_TONS AS MAX_VEHICLE_TONS,
                       MIN(P.ZONE_TIME_PLAN_IN) AS TIME_FROM,
                       MAX(P.ZONE_TIME_PLAN_OUT) AS TIME_TO,
                       NVL(A.TW_STRICT, 0) AS TW_STRICT,
                       NVL(A.UNLOAD_NORM_MIN, 30) AS UNLOAD_NORM_MIN,
                       NVL(ROUND(COUNT(DISTINCT CASE WHEN NVL(P.PROOVED,0) = 1 OR NVL(P.PROOVED_BY_SCAN,0) = 1
                                      THEN P.ID END) * 100 / NULLIF(COUNT(DISTINCT P.ID), 0), 0), 0) AS VERIFY_PERC,
                       MIN(P.STDATE) AS STDATE
                  FROM RABAEV.RRL_SBORKA_PALLETS P
                  JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
                  LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
                  {where_sql}
                 GROUP BY P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD, A.SHIROTA, A.DOLGOTA,
                          P.WARE_ID, A.TRANSPORT_TYPE, A.STOL, A.MAX_VEHICLE_TONS,
                          A.TW_STRICT, A.UNLOAD_NORM_MIN
                 ORDER BY NVL(A.REGION, P.ADDR) NULLS LAST, P.ST_NUMBER
                """,
                params,
            )
            normalized = [_fill_visible_time_window(dict(row)) for row in rows]
            _REF_CACHE[cache_key] = (time.monotonic(), [dict(row) for row in normalized])
        return normalized

    def get_routing_status(self) -> dict[str, Any]:
        """Возвращает статус геокодирования адресов."""
        from .routing import HaversineProvider, OsrmProvider, ValhallaProvider, get_active_provider

        cache_key = ("routing_status",)
        now = time.monotonic()
        with _REF_CACHE_LOCK:
            cached = _REF_CACHE.get(cache_key)
            if cached and now - cached[0] <= _REF_CACHE_TTL_SEC:
                return dict(cached[1][0])

        active_provider = get_active_provider()
        osrm_available = OsrmProvider().is_available()
        valhalla_available = ValhallaProvider().is_available()
        haversine_available = HaversineProvider().is_available()
        rows = self.gateway.fetch_all(
            """
            SELECT COUNT(*)                                                AS TOTAL_ADDRS,
                   SUM(CASE WHEN SHIROTA IS NOT NULL AND SHIROTA <> 0
                            THEN 1 ELSE 0 END)                            AS GEOCODED
              FROM RABAEV.RRL_ADDR
            """
        )
        total = int(rows[0]["TOTAL_ADDRS"] or 0) if rows else 0
        geocoded = int(rows[0]["GEOCODED"] or 0) if rows else 0
        result = {
            "provider": active_provider.name,
            "provider_available": True,
            "active_provider": active_provider.name,
            "osrm_available": osrm_available,
            "valhalla_available": valhalla_available,
            "haversine_available": haversine_available,
            "total_addresses": total,
            "geocoded_count": geocoded,
            "ungeocoded_count": total - geocoded,
        }
        with _REF_CACHE_LOCK:
            _REF_CACHE[cache_key] = (time.monotonic(), [dict(result)])
        return result

    # ------------------------------------------------------------------
    # Паллеты СТ (Sprint 6)
    # ------------------------------------------------------------------

    def list_st_pallets(self, st_number: str) -> list[dict[str, Any]]:
        """Возвращает плоский список строк паллет для СТ — группировка по PALLET_UID на фронте."""
        return self.gateway.fetch_all(
            """
            SELECT SP.PALLET_UID, SP.ZONE, SP.LOAD_TYPE, SP.ORD,
                   R.ARTICUL,
                   ROUND(NVL(R.ORDER_WEIGHT, 0), 0)                          AS ORDER_WEIGHT,
                   NVL(R.PACK_COUNT, 0)                                       AS PACK_COUNT,
                   ROUND(NVL(R.TARESIZE, 0) * NVL(R.PACK_COUNT, 0) / 1000000, 3) AS ROW_VOLUME_M3
              FROM RABAEV.RRL_SBORKA_PALLETS SP
             LEFT JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = SP.PALLET_UID
             WHERE SP.ST_NUMBER = :st_number
               AND NVL(SP.CONDITION, 0) <> 2
             ORDER BY SP.ORD NULLS LAST, SP.PALLET_UID, R.ARTICUL
            """,
            {"st_number": st_number},
        )

    # ------------------------------------------------------------------
    # VRP — Sprint 8
    # ------------------------------------------------------------------

    def solve_vrp(
        self,
        plan_date: date,
        ware_ids: list[int] | None = None,
        transport_type: str | None = None,
        time_limit_s: int = 30,
        source: str = "auto",
        solver: str = "auto",
        cancel_event: "threading.Event | None" = None,
    ) -> VrpPlanResponse:
        """Запускает VRP-решатель, сохраняет план и возвращает ответ."""
        from .vrp_solver import VrpOrder, VrpVehicle, solve as vrp_solve
        from .routing import get_active_provider

        started_at = time.perf_counter()
        requested_solver = solver
        explain_steps: list[dict[str, Any]] = []
        explain_warnings: list[dict[str, Any]] = []
        active_provider_name = get_active_provider().name

        # Load orders
        raw_orders = self.get_planner_orders(
            plan_date=plan_date,
            ware_ids=ware_ids,
            transport_type=transport_type,
        )
        orders_with_coords = sum(1 for o in raw_orders if o.get("LAT") and o.get("LON"))
        fallback_tw_count = 0
        orders: list[VrpOrder] = []
        for o in raw_orders:
            if not o.get("LAT") or not o.get("LON"):
                continue
            fallback_from, fallback_to = _fallback_time_window_from_ord(o.get("ORD"))
            has_real_tw = o.get("TIME_FROM") is not None and o.get("TIME_TO") is not None
            if not has_real_tw:
                fallback_tw_count += 1
            orders.append(
                VrpOrder(
                    st_number=o["ST_NUMBER"],
                    addr=o["ADDR"] or "",
                    lat=float(o["LAT"]) if o.get("LAT") else 0.0,
                    lon=float(o["LON"]) if o.get("LON") else 0.0,
                    pallets=int(o.get("PALLETS_COUNT") or 0),
                    weight_kg=float(o.get("WEIGHT_KG") or 0),
                    ware_id=int(o.get("WARE_ID") or 0),
                    transport_type=o.get("TRANSPORT_TYPE"),
                    tw_from=int(_minutes_from_shift_start(o.get("TIME_FROM"), default=fallback_from)),
                    tw_to=int(_minutes_from_shift_start(o.get("TIME_TO"), default=fallback_to)),
                    tw_strict=bool(o.get("TW_STRICT")),
                    unload_norm_min=int(o.get("UNLOAD_NORM_MIN") or 30),
                )
            )
        explain_steps.append({
            "code": "orders_loaded",
            "status": "done" if raw_orders else "warning",
            "label": "Заявки загружены",
            "message": f"Найдено {len(raw_orders)} СТ, {orders_with_coords} с координатами",
            "elapsed_ms": int((time.perf_counter() - started_at) * 1000),
        })
        if len(raw_orders) != orders_with_coords:
            explain_warnings.append({
                "code": "orders_without_coords",
                "severity": "warning",
                "message": f"{len(raw_orders) - orders_with_coords} СТ не попали в расчет из-за отсутствия координат",
                "action": "Проверить геокодирование адресов",
            })
        if fallback_tw_count:
            explain_warnings.append({
                "code": "time_window_fallback",
                "severity": "warning",
                "message": f"Для {fallback_tw_count} СТ временные окна рассчитаны fallback-правилом по ORD",
                "action": "Проверить ZONE_TIME_PLAN_IN/OUT в Oracle",
            })

        # Load vehicles
        raw_vehicles = self.list_vehicles(active_only=True)
        vehicles = [
            VrpVehicle(
                id=int(v["ID"]),
                num=str(v["NUM"] or ""),
                tr_type=str(v.get("TR_TYPE") or ""),
                max_pallets=int(v.get("PALLETS") or 0),
                max_tons=float(v.get("MAX_WEIGHT_KG") or 0)/1000,
                gidrobort=bool(v.get("GIDROBORT")),
            )
            for v in raw_vehicles if float(v.get("PALLETS")or 0)>0 and float(v.get("MAX_WEIGHT_KG")or 0)>0
        ]

        if not vehicles:
            raise HTTPException(status_code=422, detail="Нет действующих ТС с заданной паллетной и весовой вместимостью")
        explain_steps.append({
            "code": "vehicles_loaded",
            "status": "done",
            "label": "Машины загружены",
            "message": f"Доступно {len(vehicles)} активных ТС",
            "elapsed_ms": int((time.perf_counter() - started_at) * 1000),
        })

        # Load distance cache
        from ..modules.transport.public import planner_inputs
        dist_cache,duration_cache,used_provider_name,origin=planner_inputs(self.gateway,orders)
        matrix_pairs=len(dist_cache)
        explain_steps.append({
            "code": "distance_matrix_loaded",
            "status": "done" if matrix_pairs else "warning",
            "label": "Матрица расстояний",
            "message": f"Загружено {matrix_pairs} пар, provider: {used_provider_name}; адрес отправления: "+("настроен"if origin else "виртуальное депо"),
            "elapsed_ms": int((time.perf_counter() - started_at) * 1000),
        })
        if source == "auto" and active_provider_name != used_provider_name and used_provider_name == "haversine":
            explain_warnings.append({
                "code": "routing_fallback",
                "severity": "warning",
                "message": "Для расчета использован Haversine fallback или пустая матрица расстояний",
                "action": "Проверить OSRM/Valhalla и пересчитать матрицу",
            })

        # Sprint 117 — Attention Model solver
        if solver == "attention_model":
            from .am_solver import is_available as am_available, solve_am
            if am_available():
                lats = [o.lat for o in orders]
                lons = [o.lon for o in orders]
                palls = [o.pallets for o in orders]
                am_route = solve_am(lats, lons, palls)
                if am_route is not None:
                    # Reorder orders by AM result and wrap in a single-vehicle plan
                    ordered_orders = [orders[i] for i in am_route if i < len(orders)]
                    from .vrp_solver import VrpPlan as _VrpPlanInner, VrpRoute as _VrpRouteInner
                    plan = _VrpPlanInner(
                        solver_used="attention_model",
                        routes=[_VrpRouteInner(
                            vehicle=vehicles[0],
                            stops=ordered_orders,
                            total_km=0,
                            total_pallets=sum(o.pallets for o in ordered_orders),
                        )],
                        score=0.0,
                    )
                    # Fall through to save plan
                else:
                    solver = "auto"  # fallback
            else:
                solver = "auto"  # fallback if no model

        if solver != "attention_model":
            # Solve
            plan = vrp_solve(
                orders=orders,
                vehicles=vehicles,
                dist_cache=dist_cache or None,duration_cache=duration_cache or None,origin=origin,
                time_limit_s=time_limit_s,
                solver=solver,
            )
        explain_steps.append({
            "code": "optimization_done",
            "status": "done" if plan.routes else "warning",
            "label": "Оптимизация завершена",
            "message": f"Построено {len(plan.routes)} рейсов, без рейса {len(plan.unassigned)} СТ",
            "elapsed_ms": int((time.perf_counter() - started_at) * 1000),
        })
        if plan.unassigned:
            explain_warnings.append({
                "code": "unassigned_sts",
                "severity": "warning",
                "message": f"{len(plan.unassigned)} СТ не назначены в рейсы",
                "action": "Открыть список СТ без рейса и проверить ограничения",
            })
        if plan.tw_violations:
            explain_warnings.append({
                "code": "tw_violations",
                "severity": "warning",
                "message": f"Найдено нарушений временных окон: {plan.tw_violations}",
                "action": "Раскрыть рейсы с нарушениями окон",
            })

        route_utils = [r.utilization_pct for r in plan.routes]
        low_utilization_routes = sum(1 for value in route_utils if value < 60)
        over_capacity_routes = sum(1 for value in route_utils if value > 100)
        if low_utilization_routes:
            explain_warnings.append({
                "code": "low_utilization_routes",
                "severity": "info",
                "message": f"{low_utilization_routes} рейсов имеют загрузку ниже 60%",
                "action": "Проверить возможность объединения или переноса",
            })
        if over_capacity_routes:
            explain_warnings.append({
                "code": "over_capacity_routes",
                "severity": "error",
                "message": f"{over_capacity_routes} рейсов превышают вместимость машины",
                "action": "Не применять план без ручной корректировки",
            })

        from ..modules.transport.contracts import route_payload, route_response, planner_constraint_evidence
        # Save plan to Oracle
        explain = {
            "input": {
                "plan_date": str(plan_date),
                "orders_total": len(raw_orders),
                "orders_with_coords": orders_with_coords,
                "orders_skipped_no_coords": max(0, len(raw_orders) - orders_with_coords),
                "ware_ids": ware_ids or [],
                "transport_type": transport_type,
            },
            "routing": {
                "requested_source": source,
                "active_provider": active_provider_name,
                "used_provider": used_provider_name,
                "fallback_used": bool(
                    (source == "auto" and used_provider_name == "haversine" and active_provider_name != "haversine")
                    or not matrix_pairs
                ),
                "matrix_pairs": matrix_pairs,
                "matrix_age_min": None,
            },
            "solver": {
                "requested_solver": requested_solver,
                "used_solver": plan.solver_used,
                "time_limit_s": time_limit_s,
                "solve_time_ms": plan.solve_time_ms,
            },
            "constraints": planner_constraint_evidence(plan.routes, fallback_tw_count),
            "fleet": {
                "vehicles_total": len(vehicles),
                "vehicles_used": len(plan.routes),
                "target_routes_per_vehicle": 4,
                "target_daily_routes": len(vehicles) * 4,
                "planned_routes": len(plan.routes),
                "avg_utilization_pct": round(sum(route_utils) / len(route_utils), 1) if route_utils else 0.0,
                "min_utilization_pct": min(route_utils) if route_utils else 0.0,
                "max_utilization_pct": max(route_utils) if route_utils else 0.0,
                "low_utilization_routes": low_utilization_routes,
                "over_capacity_routes": over_capacity_routes,
            },
            "steps": explain_steps,
            "warnings": explain_warnings,
        }
        plan_json = json.dumps(
            {
                "solver": plan.solver_used,
                "routes": [route_payload(r) for r in plan.routes],
                "unassigned": [o.st_number for o in plan.unassigned],
                "total_km": plan.total_km,
                "fleet_utilization_pct": plan.fleet_utilization_pct,
                "tw_violations": plan.tw_violations,
                "score": plan.score,
                "explain": explain,
            },
            ensure_ascii=False,
        )
        # Get next ID from sequence, then insert
        seq_row = self.gateway.fetch_all("SELECT SEQ_PLANNER_PLANS.NEXTVAL AS NV FROM DUAL")
        plan_id: int | None = int(seq_row[0]["NV"]) if seq_row else None

        if plan_id is not None:
            self.gateway.execute(
                """
                INSERT INTO RABAEV.RRL_PLANNER_PLANS
                       (ID, PLAN_DATE, CREATED_AT, SOLVER, SCORE, PAYLOAD)
                VALUES (:plan_id, :plan_date, SYSDATE, :solver, :score, :plan_json)
                """,
                {
                    "plan_id":   plan_id,
                    "plan_date": plan_date,
                    "solver":    plan.solver_used,
                    "score":     plan.score,
                    "plan_json": plan_json,
                },
            )

        # Build response
        route_items = [VrpRouteItem(**route_response(r)) for r in plan.routes]
        explain_steps.append({
            "code": "plan_saved",
            "status": "done" if plan_id is not None else "warning",
            "label": "План сохранен",
            "message": f"plan_id={plan_id}" if plan_id is not None else "План рассчитан без сохранения",
            "elapsed_ms": int((time.perf_counter() - started_at) * 1000),
        })

        return VrpPlanResponse(
            plan_id=plan_id,
            routes=route_items,
            unassigned_sts=[o.st_number for o in plan.unassigned],
            total_km=plan.total_km,
            fleet_utilization_pct=plan.fleet_utilization_pct,
            tw_violations=plan.tw_violations,
            score=plan.score,
            solver_used=plan.solver_used,
            solve_time_ms=plan.solve_time_ms,
            explain=explain,
        )

    def apply_vrp_plan(self, plan_id: int, shipment_date: date, dock: str | None, user_id: str) -> dict[str, Any]:
        from ..modules.transport.public import apply_existing_plan,TransportPlanError
        try:
            result=apply_existing_plan(self.gateway,plan_id,shipment_date,dock,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_available_sts_cache()
        for trip in result["created_task_ids"]:_clear_task_sts_cache(trip)
        return result

    def get_plan_metrics(self, plan_id: int | None = None) -> dict[str, Any]:
        """Возвращает метрики плана. plan_id=None → последний план."""
        if plan_id is None:
            rows = self.gateway.fetch_all(
                """
                SELECT ID, PLAN_DATE, SOLVER, SCORE, PAYLOAD AS PLAN_JSON, CREATED_AT, APPLIED_AT
                  FROM RABAEV.RRL_PLANNER_PLANS
                 ORDER BY ID DESC
                 FETCH FIRST 1 ROWS ONLY
                """
            )
        else:
            rows = self.gateway.fetch_all(
                """
                SELECT ID, PLAN_DATE, SOLVER, SCORE, PAYLOAD AS PLAN_JSON, CREATED_AT, APPLIED_AT
                  FROM RABAEV.RRL_PLANNER_PLANS
                 WHERE ID = :plan_id
                """,
                {"plan_id": plan_id},
            )

        if not rows:
            return {
                "plan_id": None,
                "routes": 0,
                "total_km": 0.0,
                "fleet_utilization_pct": 0.0,
                "tw_violations": 0,
                "score": 0.0,
                "solver_used": "none",
                "applied": False,
                "plan_date": None,
                "explain": None,
            }

        row = rows[0]
        plan_data = json.loads(row["PLAN_JSON"] or "{}")
        return {
            "plan_id": int(row["ID"]),
            "routes": len(plan_data.get("routes", [])),
            "total_km": float(plan_data.get("total_km") or 0),
            "fleet_utilization_pct": float(plan_data.get("fleet_utilization_pct") or 0),
            "tw_violations": int(plan_data.get("tw_violations") or 0),
            "score": float(plan_data.get("score") or 0),
            "solver_used": plan_data.get("solver", row.get("SOLVER") or "none"),
            "applied": row.get("APPLIED_AT") is not None,
            "plan_date": str(row["PLAN_DATE"])[:10] if row.get("PLAN_DATE") else None,
            "explain": plan_data.get("explain"),
        }

    # ------------------------------------------------------------------
    # Templates / history matching (Sprint 9)
    # ------------------------------------------------------------------

    def get_plan_templates(
        self,
        plan_date: date,
        lookback_days: int = 90,
        min_jaccard: float = 0.7,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Находит исторические планы, похожие на сегодняшний набор адресов,
        используя Jaccard similarity по ST_NUMBER.

        Возвращает список шаблонов: plan_id, plan_date, score, jaccard, routes_count.
        """
        # Current day ST numbers
        current_sts = self.get_planner_orders(plan_date=plan_date)
        current_set = {r["ST_NUMBER"] for r in current_sts if r.get("ST_NUMBER")}
        if not current_set:
            return []

        # Historical plans from last lookback_days, applied only
        rows = self.gateway.fetch_all(
            """
            SELECT ID, PLAN_DATE, PAYLOAD AS PLAN_JSON, SCORE
              FROM RABAEV.RRL_PLANNER_PLANS
             WHERE PLAN_DATE >= :since
               AND PLAN_DATE < :plan_date
             ORDER BY SCORE DESC
             FETCH FIRST 50 ROWS ONLY
            """,
            {
                "since": date.fromordinal(plan_date.toordinal() - lookback_days),
                "plan_date": plan_date,
            },
        )

        results = []
        for row in rows:
            try:
                plan_data = json.loads(row.get("PLAN_JSON") or "{}")
            except Exception:
                continue
            hist_sts: set[str] = set()
            for route in plan_data.get("routes", []):
                hist_sts.update(route.get("stops", []))
            if not hist_sts:
                continue
            intersection = len(current_set & hist_sts)
            union = len(current_set | hist_sts)
            jaccard = intersection / union if union else 0.0
            if jaccard < min_jaccard:
                continue
            results.append({
                "plan_id": int(row["ID"]),
                "plan_date": str(row["PLAN_DATE"])[:10],
                "score": float(row.get("SCORE") or 0),
                "jaccard": round(jaccard, 3),
                "routes_count": len(plan_data.get("routes", [])),
                "matched_sts": intersection,
                "total_current_sts": len(current_set),
            })

        results.sort(key=lambda x: x["jaccard"], reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------
    # History + demand forecast (Sprint 10)
    # ------------------------------------------------------------------

    def get_plan_history(
        self,
        date_from: date,
        date_to: date,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """История применённых планов за период с метриками Score, утилизация, пробег."""
        bounded_limit = max(1, min(int(limit or 25), 500))
        cache_key = ("planner_history", date_from, date_to, bounded_limit)
        now = time.monotonic()
        with _REF_CACHE_LOCK:
            cached = _REF_CACHE.get(cache_key)
            if cached and now - cached[0] <= _REF_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]
            rows = self.gateway.fetch_all(
                """
                SELECT ID, PLAN_DATE, SOLVER, SCORE, PAYLOAD AS PLAN_JSON, CREATED_AT, APPLIED_AT
                  FROM RABAEV.RRL_PLANNER_PLANS
                 WHERE PLAN_DATE >= :date_from
                   AND PLAN_DATE <= :date_to
                 ORDER BY PLAN_DATE DESC, ID DESC
                 FETCH FIRST :limit ROWS ONLY
                """,
                {"date_from": date_from, "date_to": date_to, "limit": bounded_limit},
            )
            result = []
            for row in rows:
                try:
                    plan_data = json.loads(row.get("PLAN_JSON") or "{}")
                except Exception:
                    plan_data = {}
                result.append({
                    "plan_id": int(row["ID"]),
                    "plan_date": str(row["PLAN_DATE"])[:10],
                    "solver": plan_data.get("solver", row.get("SOLVER") or "none"),
                    "score": float(plan_data.get("score") or row.get("SCORE") or 0),
                    "routes": len(plan_data.get("routes", [])),
                    "total_km": float(plan_data.get("total_km") or 0),
                    "fleet_utilization_pct": float(plan_data.get("fleet_utilization_pct") or 0),
                    "tw_violations": int(plan_data.get("tw_violations") or 0),
                    "applied": row.get("APPLIED_AT") is not None,
                })
            _REF_CACHE[cache_key] = (time.monotonic(), [dict(row) for row in result])
        return result

    def get_demand_forecast(
        self,
        target_date: date,
        lookback_weeks: int = 8,
    ) -> dict[str, Any]:
        """
        Прогноз числа СТ на целевую дату по историческим данным аналогичного дня недели.
        Использует COUNT(*) из RRL_V_AVAILABLE_STS за предыдущие N недель того же дня.
        """
        cache_key = ("demand_forecast", target_date, lookback_weeks)
        now = time.monotonic()
        with _REF_CACHE_LOCK:
            cached = _REF_CACHE.get(cache_key)
            if cached and now - cached[0] <= _REF_CACHE_TTL_SEC:
                return dict(cached[1][0])

        dow = target_date.weekday()  # 0=Mon … 6=Sun
        # Build list of same-weekday dates going back
        sample_dates = [
            date.fromordinal(target_date.toordinal() - 7 * (i + 1))
            for i in range(lookback_weeks)
        ]
        counts: list[int] = []
        for sample_date in sample_dates:
            rows = self.gateway.fetch_all(
                """
                SELECT COUNT(DISTINCT ST_NUMBER) AS CNT
                  FROM RABAEV.RRL_SBORKA_PALLETS
                 WHERE STDATE >= :stdate
                   AND STDATE < :stdate_next
                   AND TRANSTASK_ID IS NULL
                """,
                {
                    "stdate": sample_date,
                    "stdate_next": sample_date + timedelta(days=1),
                },
            )
            if rows:
                counts.append(int(rows[0]["CNT"] or 0))

        if not counts:
            result = {
                "target_date": str(target_date),
                "day_of_week": dow,
                "forecast_sts": 0,
                "confidence": "none",
                "samples": 0,
            }
            with _REF_CACHE_LOCK:
                _REF_CACHE[cache_key] = (time.monotonic(), [dict(result)])
            return result

        avg = round(sum(counts) / len(counts), 0)
        stddev = (sum((c - avg) ** 2 for c in counts) / len(counts)) ** 0.5
        confidence = "high" if stddev < avg * 0.15 else "medium" if stddev < avg * 0.3 else "low"

        result = {
            "target_date": str(target_date),
            "day_of_week": dow,
            "forecast_sts": int(avg),
            "confidence": confidence,
            "samples": len(counts),
            "sample_counts": counts,
            "stddev": round(stddev, 1),
        }
        with _REF_CACHE_LOCK:
            _REF_CACHE[cache_key] = (time.monotonic(), [dict(result)])
        return result

    # ------------------------------------------------------------------
    # Sprint 11 — ARM: операции и нормативы
    # ------------------------------------------------------------------

    def _load_norms(self) -> dict[str, dict]:
        """Загружает нормативы из RRL_TRANSPORT_NORMS → {code: {dur, per_unit}}."""
        rows = _cached_ref(
            ("transport_norms", None),
            lambda: self.gateway.fetch_all(
                "SELECT OPERATION_CODE, DURATION_MIN, PER_UNIT FROM RABAEV.RRL_TRANSPORT_NORMS"
            ),
        )
        return {
            r["OPERATION_CODE"]: {
                "duration_min": float(r["DURATION_MIN"]),
                "per_unit": int(r["PER_UNIT"] or 0),
            }
            for r in rows
        }

    def plan_operations(self, task_id: int, user_id: str) -> list[dict[str,Any]]:
        from ..modules.transport.public import generate_existing_operations,TransportPlanError
        try:
            result=generate_existing_operations(self.gateway,task_id,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_vehicle_availability_cache()
        return result

    def get_operations(self, task_id: int) -> list[dict]:
        """Список операций рейса с расчётом отклонения."""
        rows = self.gateway.fetch_all(
            """
            SELECT ID, TT_ID, OPERATION_CODE, ORD, DURATION_MIN,
                   TO_CHAR(PLAN_START, 'YYYY-MM-DD HH24:MI') AS PLAN_START,
                   TO_CHAR(PLAN_END,   'YYYY-MM-DD HH24:MI') AS PLAN_END,
                   TO_CHAR(FACT_START, 'YYYY-MM-DD HH24:MI') AS FACT_START,
                   TO_CHAR(FACT_END,   'YYYY-MM-DD HH24:MI') AS FACT_END,
                   NOTE
              FROM RABAEV.RRL_TT_OPERATIONS
             WHERE TT_ID = :tt_id
             ORDER BY ORD
            """,
            {"tt_id": task_id},
        )

        return [self._operation_row_to_dict(r) for r in rows]

    def _operation_row_to_dict(self, r: dict[str, Any]) -> dict[str, Any]:
        from datetime import datetime as dt

        def _parse(value: Any):
            return dt.strptime(str(value), "%Y-%m-%d %H:%M") if value else None

        delta = None
        if r.get("FACT_END") and r.get("PLAN_END"):
            delta = round((_parse(r["FACT_END"]) - _parse(r["PLAN_END"])).total_seconds() / 60, 1)
        return {
            "op_id": int(r["ID"]),
            "tt_id": int(r["TT_ID"]),
            "operation_code": r["OPERATION_CODE"],
            "ord": int(r["ORD"]),
            "duration_min": float(r["DURATION_MIN"] or 0),
            "plan_start": r.get("PLAN_START"),
            "plan_end": r.get("PLAN_END"),
            "fact_start": r.get("FACT_START"),
            "fact_end": r.get("FACT_END"),
            "delta_min": delta,
            "note": r.get("NOTE"),
        }

    def update_operation_fact(self, op_id: int, data: OperationFactUpdate, user_id: str) -> dict[str,Any]:
        from ..modules.transport.public import update_existing_operation_fact,TransportPlanError
        fields=data.model_dump(exclude_none=True,mode="json")
        if not fields:raise HTTPException(status_code=400,detail="Нет полей для обновления")
        try:
            result=update_existing_operation_fact(self.gateway,op_id,fields,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_vehicle_availability_cache()
        return result

    def get_vehicles_gantt(self, gantt_date: date) -> list[dict]:
        """Данные Ганта для всех машин на день."""
        rows = self.gateway.fetch_all(
            """
            SELECT TT.ID AS TT_ID, TT.TRANSPORT AS VEHICLE_NUM, TT.TRANSTYPE AS VEHICLE_TYPE,
                   V.ID AS VEHICLE_ID,
                   OPS.ID, OPS.OPERATION_CODE, OPS.ORD, OPS.DURATION_MIN,
                   TO_CHAR(OPS.PLAN_START, 'YYYY-MM-DD HH24:MI') AS PLAN_START,
                   TO_CHAR(OPS.PLAN_END,   'YYYY-MM-DD HH24:MI') AS PLAN_END,
                   TO_CHAR(OPS.FACT_START, 'YYYY-MM-DD HH24:MI') AS FACT_START,
                   TO_CHAR(OPS.FACT_END,   'YYYY-MM-DD HH24:MI') AS FACT_END,
                   OPS.NOTE
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TR_VEHICLE V ON V.NUM = TT.TRANSPORT
              JOIN RABAEV.RRL_TT_OPERATIONS OPS ON OPS.TT_ID = TT.ID
             WHERE TT.SHIPMENT_DATE >= TO_DATE(:d, 'YYYY-MM-DD')
               AND TT.SHIPMENT_DATE <  TO_DATE(:d, 'YYYY-MM-DD') + 1
               AND NVL(TT.DELETED, 0) = 0
             ORDER BY NVL(TT.TRANSPORT, ' '), TT.ID, OPS.ORD
            """,
            {"d": str(gantt_date)},
        )

        result = []
        by_vehicle: dict[str, dict[str, Any]] = {}
        for row in rows:
            tt_id = int(row["TT_ID"])
            vnum = row.get("VEHICLE_NUM") or ""
            vehicle_key = vnum or f"task:{tt_id}"
            entry = by_vehicle.get(vehicle_key)
            if entry is None:
                entry = {
                    "_vehicle_key": vehicle_key,
                    "vehicle_id": int(row["VEHICLE_ID"] or 0),
                    "vehicle_num": vnum,
                    "vehicle_type": row.get("VEHICLE_TYPE") or "",
                    "operations": [],
                }
                by_vehicle[vehicle_key] = entry
                result.append(entry)
            entry["operations"].append(
                self._operation_row_to_dict(
                    {
                        "ID": row["ID"],
                        "TT_ID": row["TT_ID"],
                        "OPERATION_CODE": row["OPERATION_CODE"],
                        "ORD": row["ORD"],
                        "DURATION_MIN": row["DURATION_MIN"],
                        "PLAN_START": row["PLAN_START"],
                        "PLAN_END": row["PLAN_END"],
                        "FACT_START": row["FACT_START"],
                        "FACT_END": row["FACT_END"],
                        "NOTE": row["NOTE"],
                    }
                )
            )

        for entry in result:
            entry.pop("_vehicle_key", None)
        return result

    # ------------------------------------------------------------------
    # Sprint 13 — Умный подбор машины и конфликты
    # ------------------------------------------------------------------

    def get_vehicles_available(self, shipment_time: str, pallets: int) -> list[dict]:
        """Возвращает список машин с индикатором доступности к времени отгрузки.

        Проверки:
          1. Машина не занята в запрашиваемый интервал (текущая занятость).
          2. CLEAN_RETURNS.PLAN_END завершена до shipment_time (освобождение).
          3. Вместимость машины достаточна для переданного числа паллет.
          4. Машина не заблокирована (BLOCKED = 0).

        Статус:
          green  — машина свободна к shipment_time
          yellow — освобождается < 60 мин позже
          red    — освободится > 60 мин позже или не хватает паллет
        """
        from datetime import datetime as dt

        try:
            requested_dt = dt.strptime(shipment_time[:16], "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=422, detail="shipment_time must be YYYY-MM-DD HH:MM")

        ship_date = requested_dt.date()
        cache_key = (requested_dt.strftime("%Y-%m-%d %H:%M"), int(pallets or 0))
        now = time.monotonic()
        with _VEHICLE_AVAILABILITY_CACHE_LOCK:
            cached = _VEHICLE_AVAILABILITY_CACHE.get(cache_key)
            if cached and now - cached[0] <= _VEHICLE_AVAILABILITY_CACHE_TTL_SEC:
                return [dict(row) for row in cached[1]]

        # Last PLAN_END per vehicle for that day (from RRL_TT_OPERATIONS via task join)
        rows = self.gateway.fetch_all(
            """
            SELECT V.NUM AS VEHICLE_NUM, V.ID AS VEHICLE_ID, V.MARKA, V.TR_TYPE,
                   V.PALLETS AS MAX_PALLETS, V.GIDROBORT,
                   MAX(TO_CHAR(OPS.PLAN_END, 'YYYY-MM-DD HH24:MI')) AS LAST_OP_END
              FROM RABAEV.RRL_TR_VEHICLE V
              LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT
                ON TT.TRANSPORT = V.NUM
               AND TT.SHIPMENT_DATE >= TO_DATE(:d, 'YYYY-MM-DD')
               AND TT.SHIPMENT_DATE <  TO_DATE(:d, 'YYYY-MM-DD') + 1
               AND NVL(TT.DELETED, 0) = 0
              LEFT JOIN RABAEV.RRL_TT_OPERATIONS OPS
                ON OPS.TT_ID = TT.ID
             WHERE V.BLOCKED = 0
             GROUP BY V.NUM, V.ID, V.MARKA, V.TR_TYPE, V.PALLETS, V.GIDROBORT
             ORDER BY V.TR_TYPE, V.NUM
            """,
            {"d": str(ship_date)},
        )

        result = []
        for r in rows:
            last_end_str = r.get("LAST_OP_END")
            max_pallets = int(r.get("MAX_PALLETS") or 0)

            # Pallet capacity check
            capacity_ok = max_pallets == 0 or max_pallets >= pallets

            if last_end_str:
                try:
                    last_end_dt = dt.strptime(last_end_str[:16], "%Y-%m-%d %H:%M")
                except ValueError:
                    last_end_dt = None
            else:
                last_end_dt = None

            if last_end_dt is None:
                # No operations for this day → free all day
                free_at = None
                delay_min = 0
            else:
                delay_min = (last_end_dt - requested_dt).total_seconds() / 60
                free_at = last_end_dt.strftime("%H:%M")

            if not capacity_ok:
                status = "red"
                detail = f"Паллет {max_pallets}, запрошено {pallets}"
            elif delay_min <= 0:
                status = "green"
                detail = "Свободна"
            elif delay_min <= 60:
                status = "yellow"
                detail = f"Освободится в {free_at}"
            else:
                status = "red"
                detail = f"Занята до {free_at}"

            result.append(
                {
                    "vehicle_id": int(r.get("VEHICLE_ID") or 0),
                    "vehicle_num": r.get("VEHICLE_NUM") or "",
                    "vehicle_type": r.get("TR_TYPE") or "",
                    "marka": r.get("MARKA") or "",
                    "max_pallets": max_pallets,
                    "gidrobort": bool(r.get("GIDROBORT")),
                    "free_at": free_at,
                    "delay_min": round(delay_min, 0),
                    "status": status,
                    "detail": detail,
                }
            )

        # Sort: green first, then yellow, then red
        order = {"green": 0, "yellow": 1, "red": 2}
        result.sort(key=lambda x: (order.get(x["status"], 3), x["vehicle_num"]))
        with _VEHICLE_AVAILABILITY_CACHE_LOCK:
            _VEHICLE_AVAILABILITY_CACHE[cache_key] = (time.monotonic(), [dict(row) for row in result])
        return result

    # ------------------------------------------------------------------
    # Sprint 15 — Биллинг: создание счёта
    # ------------------------------------------------------------------

    def list_billing_orders(
        self,
        company: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        closed: int | None = None,
        payed: int | None = None,
    ) -> list[dict]:
        """Список биллинг-заказов с суммой и числом рейсов."""
        conditions = ["1=1"]
        params: dict[str, Any] = {}
        if company:
            conditions.append("UPPER(B.COMPANY) LIKE UPPER(:company)")
            params["company"] = f"%{company}%"
        if date_from:
            conditions.append("B.DATEFROM >= TO_DATE(:df, 'YYYY-MM-DD')")
            params["df"] = str(date_from)
        if date_to:
            conditions.append("B.DATETO <= TO_DATE(:dt, 'YYYY-MM-DD')")
            params["dt"] = str(date_to)
        if closed is not None:
            conditions.append("B.CLOSED = :closed")
            params["closed"] = closed
        if payed is not None:
            conditions.append("B.PAYED = :payed")
            params["payed"] = payed

        where = " AND ".join(conditions)
        rows = self.gateway.fetch_all(
            f"""
            SELECT B.ID, B.NUM, B.COMPANY, B.NUM_PLAT,
                   TO_CHAR(B.DATEOFORDER, 'YYYY-MM-DD') AS DATEOFORDER,
                   TO_CHAR(B.DATEFROM,    'YYYY-MM-DD') AS DATEFROM,
                   TO_CHAR(B.DATETO,      'YYYY-MM-DD') AS DATETO,
                   B.CLOSED, B.PAYED,
                   COUNT(TT.ID)            AS TASK_COUNT,
                   SUM(NVL(TT.PRICE, 0))  AS TOTAL_PRICE
              FROM RABAEV.RRL_BILL_ORDERS B
              LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.PAY_ORDER_ID = B.ID
             WHERE {where}
             GROUP BY B.ID, B.NUM, B.COMPANY, B.NUM_PLAT, B.DATEOFORDER, B.DATEFROM, B.DATETO, B.CLOSED, B.PAYED
             ORDER BY B.ID DESC
            """,
            params,
        )
        return [
            {
                "order_id": int(r["ID"]),
                "num": r.get("NUM"),
                "company": r.get("COMPANY"),
                "date_of_order": r.get("DATEOFORDER"),
                "date_from": r.get("DATEFROM"),
                "date_to": r.get("DATETO"),
                "closed": int(r.get("CLOSED") or 0),
                "payed": int(r.get("PAYED") or 0),
                "task_count": int(r.get("TASK_COUNT") or 0),
                "total_price": float(r.get("TOTAL_PRICE") or 0),
                "num_plat": r.get("NUM_PLAT"),
            }
            for r in rows
        ]

    def create_billing_order(self, company: str, date_from: str, date_to: str) -> int:
        """Создаёт новый биллинг-заказ и возвращает его ID."""
        rows = self.gateway.fetch_all("SELECT RABAEV.SEQ_BILL_ORDERS.NEXTVAL AS NV FROM DUAL")
        order_id = int(rows[0]["NV"])
        num = f"БТ-{order_id:04d}"
        self.gateway.execute(
            """
            INSERT INTO RABAEV.RRL_BILL_ORDERS
              (ID, NUM, COMPANY, DATEOFORDER, DATEFROM, DATETO, CLOSED, PAYED)
            VALUES
              (:id, :num, :company, SYSDATE,
               TO_DATE(:df, 'YYYY-MM-DD'), TO_DATE(:dt, 'YYYY-MM-DD'), 0, 0)
            """,
            {"id": order_id, "num": num, "company": company, "df": date_from, "dt": date_to},
        )
        return order_id

    def add_tasks_to_order(self, order_id: int, tt_ids: list[int]) -> None:
        """Привязывает рейсы к биллинг-заказу через legacy Oracle-функцию."""
        if not self.get_billing_order(order_id):
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        for tt_id in tt_ids:
            result = self.gateway.call_varchar_plsql(
                "BEGIN :result := RABAEV.RRL_ADD_TT_2_BILLINGORDER(:bill_id, :tt_id, :act); END;",
                {"bill_id": order_id, "tt_id": tt_id, "act": 1},
            )
            if result and result.lower() not in ("ok", "ок", "1", "true"):
                raise HTTPException(status_code=409, detail=result)

    def get_task_billing(self, tt_id: int) -> dict | None:
        """Возвращает данные биллинг-заказа для рейса или None."""
        rows = self.gateway.fetch_all(
            """
            SELECT B.ID, B.NUM, B.COMPANY,
                   TO_CHAR(B.DATEOFORDER, 'YYYY-MM-DD') AS DATEOFORDER,
                   TO_CHAR(B.DATEFROM,    'YYYY-MM-DD') AS DATEFROM,
                   TO_CHAR(B.DATETO,      'YYYY-MM-DD') AS DATETO,
                   B.CLOSED, B.PAYED
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              JOIN RABAEV.RRL_BILL_ORDERS B ON B.ID = TT.PAY_ORDER_ID
             WHERE TT.ID = :tt_id
            """,
            {"tt_id": tt_id},
        )
        if not rows:
            return None
        r = rows[0]
        return {
            "order_id": int(r["ID"]),
            "num": r.get("NUM"),
            "company": r.get("COMPANY"),
            "date_of_order": r.get("DATEOFORDER"),
            "date_from": r.get("DATEFROM"),
            "date_to": r.get("DATETO"),
            "closed": int(r.get("CLOSED") or 0),
            "payed": int(r.get("PAYED") or 0),
        }

    def get_billing_order(self, order_id: int) -> dict | None:
        """Один биллинг-заказ по ID."""
        rows = self.gateway.fetch_all(
            """
            SELECT B.ID, B.NUM, B.COMPANY, B.NUM_PLAT,
                   TO_CHAR(B.DATEOFORDER, 'YYYY-MM-DD') AS DATEOFORDER,
                   TO_CHAR(B.DATEFROM,    'YYYY-MM-DD') AS DATEFROM,
                   TO_CHAR(B.DATETO,      'YYYY-MM-DD') AS DATETO,
                   B.CLOSED, B.PAYED,
                   COUNT(TT.ID)           AS TASK_COUNT,
                   SUM(NVL(TT.PRICE, 0)) AS TOTAL_PRICE
              FROM RABAEV.RRL_BILL_ORDERS B
              LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.PAY_ORDER_ID = B.ID
             WHERE B.ID = :order_id
             GROUP BY B.ID, B.NUM, B.COMPANY, B.NUM_PLAT, B.DATEOFORDER, B.DATEFROM, B.DATETO, B.CLOSED, B.PAYED
            """,
            {"order_id": order_id},
        )
        if not rows:
            return None
        r = rows[0]
        return {
            "order_id": int(r["ID"]),
            "num": r.get("NUM"),
            "company": r.get("COMPANY"),
            "date_of_order": r.get("DATEOFORDER"),
            "date_from": r.get("DATEFROM"),
            "date_to": r.get("DATETO"),
            "closed": int(r.get("CLOSED") or 0),
            "payed": int(r.get("PAYED") or 0),
            "task_count": int(r.get("TASK_COUNT") or 0),
            "total_price": float(r.get("TOTAL_PRICE") or 0),
            "num_plat": r.get("NUM_PLAT"),
        }

    def close_billing_order(self, order_id: int) -> dict:
        """Закрывает биллинг-заказ через Oracle-процедуру."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        if order["closed"]:
            raise HTTPException(status_code=409, detail="Заказ уже закрыт")
        result = self.gateway.call_varchar_plsql(
            "BEGIN :result := RABAEV.RRL_CLOSE_BILLINGORDER(:bill_id, :act); END;",
            {"bill_id": order_id, "act": 1},
        )
        if result and result.lower() not in ("ok", "ок", "1", "true"):
            raise HTTPException(status_code=409, detail=result)
        return self.get_billing_order(order_id) or {"order_id": order_id, "closed": 1}

    def pay_billing_order(self, order_id: int) -> dict:
        """Отмечает биллинг-заказ как оплаченный через Oracle-процедуру."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        if order["payed"]:
            raise HTTPException(status_code=409, detail="Заказ уже оплачен")
        result = self.gateway.call_varchar_plsql(
            "BEGIN :result := RABAEV.RRL_PAY_BILLINGORDER(:bill_id, :act); END;",
            {"bill_id": order_id, "act": 1},
        )
        if result and result.lower() not in ("ok", "ок", "1", "true"):
            raise HTTPException(status_code=409, detail=result)
        return self.get_billing_order(order_id) or {"order_id": order_id, "payed": 1}

    def open_billing_for_task(self, tt_id: int) -> dict:
        """Создаёт биллинг-заказ для рейса и привязывает его.

        Компания берётся из поля DOVERENNOST_OT водителя рейса.
        Дата периода = дата отгрузки рейса.
        """
        task = self.get_task(tt_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {tt_id} not found")
        if task.get("PAY_ORDER_ID"):
            raise HTTPException(status_code=409, detail="Рейс уже включён в биллинг-заказ")

        company = task.get("TK_NAME") or task.get("DOVERENNOST_OT") or "Неизвестная ТК"
        if company == "Неизвестная ТК" or float(task.get("PRICE") or 0) <= 0:
            raise HTTPException(
                status_code=409,
                detail="Рейс не готов к биллингу: не указана ТК или не рассчитана сумма",
            )
        ship_date = str(task.get("SHIPMENT_DATE") or "")[:10]
        if not ship_date:
            from datetime import date as _date
            ship_date = str(_date.today())

        order_id = self.create_billing_order(company=company, date_from=ship_date, date_to=ship_date)
        self.add_tasks_to_order(order_id, [tt_id])

        return self.get_task_billing(tt_id) or {"order_id": order_id}

    def get_billing_order_tasks(self, order_id: int) -> list[dict]:
        """Список рейсов в биллинг-заказе."""
        if self.get_billing_order(order_id) is None:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        rows = self.gateway.fetch_all(
            """
            SELECT TT.ID, TT.TRANSPORT, TT.CONDITION AS STATUS, TT.PRICE,
                   TO_CHAR(TT.SHIPMENT_DATE, 'YYYY-MM-DD') AS SHIPMENT_DATE
              FROM RABAEV.RRL_TRANSPORT_TASK TT
             WHERE TT.PAY_ORDER_ID = :order_id
             ORDER BY TT.SHIPMENT_DATE, TT.ID
            """,
            {"order_id": order_id},
        )
        return [
            {
                "tt_id": int(r["ID"]),
                "transport": r.get("TRANSPORT"),
                "status": _normalize_task_condition(r.get("STATUS")),
                "price": float(r.get("PRICE") or 0),
                "shipment_date": r.get("SHIPMENT_DATE"),
            }
            for r in rows
        ]

    def recalculate_price(self, task_id: int) -> dict:
        """Пересчитывает и сохраняет стоимость рейса через Oracle-функцию RRL_UPDATE_PRICE."""
        task = self.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        # RRL_UPDATE_PRICE updates PRICE, so it must be called from PL/SQL, not SELECT ... FROM DUAL.
        new_price = self.gateway.call_optional_number_plsql(
            "BEGIN :result := RABAEV.RRL_UPDATE_PRICE(:tt_id); END;",
            {"tt_id": task_id},
        )
        return {"task_id": task_id, "price": float(new_price or 0)}

    def list_billing_companies(self) -> list[str]:
        """Справочник транспортных компаний из RRL_BILL_COMPANY."""
        rows = _cached_ref(
            ("billing_companies", True),
            lambda: self.gateway.fetch_all(
                """
                SELECT COMPANYNAME
                  FROM RABAEV.RRL_BILL_COMPANY
                 WHERE DELETED = 0
                 ORDER BY POS
                """
            ),
        )
        return [str(r["COMPANYNAME"]) for r in rows if r.get("COMPANYNAME")]

    def set_task_price(self, task_id: int, price: float) -> dict:
        """Ручная установка стоимости рейса (право CREATE_TT_PRICE)."""
        task = self.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        self.gateway.execute(
            "BEGIN UPDATE RABAEV.RRL_TRANSPORT_TASK SET PRICE = :price WHERE ID = :tt_id; END;",
            {"price": price, "tt_id": task_id},
        )
        return {"task_id": task_id, "price": price}

    def export_billing_order_xlsx(self, order_id: int) -> bytes:
        """Генерирует XLSX-файл с составом биллинг-заказа (Sprint 26, DoD §12 #7)."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")

        tasks = self.get_billing_order_tasks(order_id)

        try:
            import io
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            return self._export_billing_order_xlsx_zip(order_id, order, tasks)

        wb = Workbook()
        ws = wb.active
        ws.title = "Счёт"

        # ── header block ──────────────────────────────────────────────────────
        hdr_fill = PatternFill("solid", fgColor="1D4ED8")
        hdr_font = Font(color="FFFFFF", bold=True, size=11)
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        meta = [
            ("Счёт №",      order.get("num") or f"#{order_id}"),
            ("Компания",    order.get("company") or ""),
            ("Период с",    order.get("date_from") or ""),
            ("Период по",   order.get("date_to") or ""),
            ("Статус",      "Оплачен" if order.get("payed") else ("Закрыт" if order.get("closed") else "Выставлен")),
            ("Платёж №",    order.get("num_plat") or ""),
        ]
        for row_idx, (label, value) in enumerate(meta, start=1):
            ws.cell(row=row_idx, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row_idx, column=2, value=value)

        start_row = len(meta) + 2

        # ── column headers ────────────────────────────────────────────────────
        columns = ["№ рейса", "ТС", "Дата отгрузки", "Статус", "Сумма, ₽"]
        for col_idx, col_name in enumerate(columns, start=1):
            cell = ws.cell(row=start_row, column=col_idx, value=col_name)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

        # ── data rows ─────────────────────────────────────────────────────────
        total = 0.0
        for data_row, t in enumerate(tasks, start=start_row + 1):
            ws.cell(row=data_row, column=1, value=t["tt_id"]).border = border
            ws.cell(row=data_row, column=2, value=t.get("transport") or "").border = border
            ws.cell(row=data_row, column=3, value=t.get("shipment_date") or "").border = border
            ws.cell(row=data_row, column=4, value=t.get("status") or "").border = border
            price_cell = ws.cell(row=data_row, column=5, value=t.get("price") or 0)
            price_cell.border = border
            price_cell.number_format = '#,##0.00'
            total += float(t.get("price") or 0)

        # ── total row ─────────────────────────────────────────────────────────
        total_row = start_row + len(tasks) + 1
        ws.cell(row=total_row, column=4, value="Итого:").font = Font(bold=True)
        total_cell = ws.cell(row=total_row, column=5, value=total)
        total_cell.font = Font(bold=True)
        total_cell.number_format = '#,##0.00'

        # ── column widths ─────────────────────────────────────────────────────
        for col, width in zip("ABCDE", [12, 22, 16, 18, 16]):
            ws.column_dimensions[col].width = width

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def _export_billing_order_xlsx_zip(self, order_id: int, order: dict, tasks: list[dict]) -> bytes:
        """Минимальный XLSX без внешних зависимостей для окружений без openpyxl."""
        import html
        import io
        import zipfile

        def cell_ref(row: int, col: int) -> str:
            letters = ""
            while col:
                col, rem = divmod(col - 1, 26)
                letters = chr(65 + rem) + letters
            return f"{letters}{row}"

        def value_cell(row: int, col: int, value: object) -> str:
            ref = cell_ref(row, col)
            if isinstance(value, (int, float)):
                return f'<c r="{ref}"><v>{value}</v></c>'
            text = html.escape("" if value is None else str(value))
            return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'

        meta = [
            ("Счёт №", order.get("num") or f"#{order_id}"),
            ("Компания", order.get("company") or ""),
            ("Период с", order.get("date_from") or ""),
            ("Период по", order.get("date_to") or ""),
            ("Статус", "Оплачен" if order.get("payed") else ("Закрыт" if order.get("closed") else "Выставлен")),
            ("Платёж №", order.get("num_plat") or ""),
        ]
        rows: list[list[object]] = [list(row) for row in meta]
        rows.append([])
        rows.append(["№ рейса", "ТС", "Дата отгрузки", "Статус", "Сумма, ₽"])
        total = 0.0
        for task in tasks:
            price = float(task.get("price") or 0)
            total += price
            rows.append([
                task.get("tt_id"),
                task.get("transport") or "",
                task.get("shipment_date") or "",
                task.get("status") or "",
                price,
            ])
        rows.append(["", "", "", "Итого:", total])

        sheet_rows = []
        for row_idx, row in enumerate(rows, start=1):
            cells = "".join(value_cell(row_idx, col_idx, value) for col_idx, value in enumerate(row, start=1))
            sheet_rows.append(f'<row r="{row_idx}">{cells}</row>')
        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            + "".join(sheet_rows)
            + '</sheetData></worksheet>'
        )
        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Счёт" sheetId="1" r:id="rId1"/></sheets></workbook>'
        )
        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'
        )
        root_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        )

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", root_rels)
            archive.writestr("xl/workbook.xml", workbook_xml)
            archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        return buf.getvalue()

    def export_billing_registry_xlsx(
        self,
        company: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        closed: int | None = None,
        payed: int | None = None,
    ) -> bytes:
        """Генерирует XLSX-реестр всех счетов по фильтру (Sprint 27)."""
        orders = self.list_billing_orders(company, date_from, date_to, closed, payed)

        try:
            import io
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            return self._export_billing_registry_xlsx_zip(orders, company, date_from, date_to)

        wb = Workbook()
        ws = wb.active
        ws.title = "Реестр счетов"

        hdr_fill = PatternFill("solid", fgColor="1D4ED8")
        hdr_font = Font(color="FFFFFF", bold=True, size=11)
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        status_map = {(0, 0): "Выставлен", (1, 0): "Закрыт", (1, 1): "Оплачен", (0, 1): "Оплачен"}

        # filter info row
        ws.cell(row=1, column=1, value="Реестр биллинг-заказов").font = Font(bold=True, size=12)
        filters_str = " | ".join(filter(None, [
            f"Компания: {company}" if company else None,
            f"С: {date_from}" if date_from else None,
            f"По: {date_to}" if date_to else None,
        ])) or "Все счета"
        ws.cell(row=2, column=1, value=filters_str).font = Font(color="444444", size=10)

        header_row = 4
        columns = ["№ счёта", "Компания", "Период с", "Период по", "Рейсов", "Сумма ₽", "Статус", "№ платёжа", "Дата создания"]
        for col_idx, col_name in enumerate(columns, start=1):
            cell = ws.cell(row=header_row, column=col_idx, value=col_name)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

        total_sum = 0.0
        for row_idx, o in enumerate(orders, start=header_row + 1):
            status = status_map.get((int(o.get("closed") or 0), int(o.get("payed") or 0)), "—")
            price = float(o.get("total_price") or 0)
            total_sum += price
            for col_idx, val in enumerate([
                o.get("num") or f"#{o['order_id']}",
                o.get("company") or "",
                o.get("date_from") or "",
                o.get("date_to") or "",
                int(o.get("task_count") or 0),
                price,
                status,
                o.get("num_plat") or "",
                o.get("date_of_order") or "",
            ], start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border = border
                if col_idx == 6:
                    cell.number_format = '#,##0.00'

        total_row = header_row + len(orders) + 1
        ws.cell(row=total_row, column=5, value="Итого:").font = Font(bold=True)
        total_cell = ws.cell(row=total_row, column=6, value=total_sum)
        total_cell.font = Font(bold=True)
        total_cell.number_format = '#,##0.00'

        for col, width in zip("ABCDEFGHI", [16, 26, 12, 12, 8, 16, 12, 16, 14]):
            ws.column_dimensions[col].width = width

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def _export_billing_registry_xlsx_zip(
        self,
        orders: list[dict],
        company: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> bytes:
        """Минимальный XLSX-реестр без openpyxl."""
        import html
        import io
        import zipfile

        def cell_ref(row: int, col: int) -> str:
            letters = ""
            while col:
                col, rem = divmod(col - 1, 26)
                letters = chr(65 + rem) + letters
            return f"{letters}{row}"

        def value_cell(row: int, col: int, value: object) -> str:
            ref = cell_ref(row, col)
            if isinstance(value, (int, float)):
                return f'<c r="{ref}"><v>{value}</v></c>'
            text = html.escape("" if value is None else str(value))
            return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'

        status_map = {(0, 0): "Выставлен", (1, 0): "Закрыт", (1, 1): "Оплачен", (0, 1): "Оплачен"}
        filters_str = " | ".join(filter(None, [
            f"Компания: {company}" if company else None,
            f"С: {date_from}" if date_from else None,
            f"По: {date_to}" if date_to else None,
        ])) or "Все счета"
        rows: list[list[object]] = [
            ["Реестр биллинг-заказов"],
            [filters_str],
            [],
            ["№ счёта", "Компания", "Период с", "Период по", "Рейсов", "Сумма ₽", "Статус", "№ платёжа", "Дата создания"],
        ]
        total_sum = 0.0
        for order in orders:
            status = status_map.get((int(order.get("closed") or 0), int(order.get("payed") or 0)), "—")
            price = float(order.get("total_price") or 0)
            total_sum += price
            rows.append([
                order.get("num") or f"#{order['order_id']}",
                order.get("company") or "",
                order.get("date_from") or "",
                order.get("date_to") or "",
                int(order.get("task_count") or 0),
                price,
                status,
                order.get("num_plat") or "",
                order.get("date_of_order") or "",
            ])
        rows.append(["", "", "", "", "Итого:", total_sum])

        sheet_rows = []
        for row_idx, row in enumerate(rows, start=1):
            cells = "".join(value_cell(row_idx, col_idx, value) for col_idx, value in enumerate(row, start=1))
            sheet_rows.append(f'<row r="{row_idx}">{cells}</row>')
        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            + "".join(sheet_rows)
            + '</sheetData></worksheet>'
        )
        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Реестр счетов" sheetId="1" r:id="rId1"/></sheets></workbook>'
        )
        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'
        )
        root_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", root_rels)
            archive.writestr("xl/workbook.xml", workbook_xml)
            archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        return buf.getvalue()

    def remove_task_from_billing_order(self, order_id: int, tt_id: int) -> dict:
        """Отвязывает рейс от биллинг-заказа (обнуляет PAY_ORDER_ID)."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        if order.get("closed"):
            raise HTTPException(status_code=409, detail="Нельзя изменить закрытый счёт")
        if order.get("payed"):
            raise HTTPException(status_code=409, detail="Нельзя изменить оплаченный счёт")
        rowcount = self.gateway.execute(
            """
            UPDATE RABAEV.RRL_TRANSPORT_TASK
               SET PAY_ORDER_ID = NULL
             WHERE ID = :tt_id
               AND PAY_ORDER_ID = :order_id
            """,
            {"tt_id": tt_id, "order_id": order_id},
        )
        if rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Task {tt_id} not in order {order_id}")
        return {"order_id": order_id, "tt_id": tt_id, "removed": True}

    def export_tasks_xlsx(
        self,
        shipment_date: date | None = None,
        condition: str | None = None,
        task_id: int | None = None,
        transport_mask: str | None = None,
        company_mask: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        no_payments_only: bool = False,
    ) -> bytes:
        """Генерирует XLSX-список рейсов (Sprint 28, ТЗ §3 «В Excel»)."""
        tasks = self.list_tasks(
            shipment_date=shipment_date,
            condition=condition,
            task_id=task_id,
            transport_mask=transport_mask,
            company_mask=company_mask,
            date_from=date_from,
            date_to=date_to,
            no_payments_only=no_payments_only,
        )

        try:
            import io
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            return self._export_tasks_xlsx_zip(tasks, shipment_date)

        wb = Workbook()
        ws = wb.active
        ws.title = "Рейсы"

        hdr_fill = PatternFill("solid", fgColor="1D4ED8")
        hdr_font = Font(color="FFFFFF", bold=True, size=10)
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        filter_date = str(shipment_date) if shipment_date else "все даты"
        ws.cell(row=1, column=1, value=f"Рейсы: {filter_date}").font = Font(bold=True, size=12)

        columns = [
            ("Дата", "SHIPMENT_DATE", 12),
            ("#", "ID", 8),
            ("Пал.", "PALLET_COUNT", 7),
            ("Вес кг", "TEMP_WEIGHT", 10),
            ("Объём м³", "VOLUME_M3", 10),
            ("Тип ТС", "TRANSTYPE", 12),
            ("Машина", "TRANSPORT", 16),
            ("Водитель", "VODITEL_NAME", 22),
            ("ДОК", "DOCK", 10),
            ("Регионы", "REGIONS", 24),
            ("Цена ₽", "PRICE", 14),
            ("ТК", "TK_NAME", 20),
            ("Логист", "LOGIST", 14),
            ("Статус", "CONDITION", 14),
        ]

        header_row = 3
        for col_idx, (label, _field, width) in enumerate(columns, start=1):
            cell = ws.cell(row=header_row, column=col_idx, value=label)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = border
            ws.column_dimensions[chr(64 + col_idx)].width = width

        for row_idx, t in enumerate(tasks, start=header_row + 1):
            vals = [
                str(t.get("SHIPMENT_DATE") or "")[:10],
                t.get("ID"),
                t.get("PALLET_COUNT"),
                t.get("TEMP_WEIGHT"),
                t.get("VOLUME_M3"),
                t.get("TRANSTYPE"),
                t.get("TRANSPORT"),
                t.get("VODITEL_NAME"),
                t.get("DOCK"),
                t.get("REGIONS") or t.get("TEMP_REGION"),
                float(t.get("PRICE") or 0) or None,
                t.get("TK_NAME"),
                t.get("LOGIST"),
                t.get("CONDITION"),
            ]
            for col_idx, val in enumerate(vals, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border = border
                if col_idx == 11 and val is not None:
                    cell.number_format = '#,##0.00'

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def _export_tasks_xlsx_zip(self, tasks: list[dict], shipment_date: date | None) -> bytes:
        """Минимальный XLSX-список рейсов без openpyxl."""
        import html
        import io
        import zipfile

        def cell_ref(row: int, col: int) -> str:
            letters = ""
            while col:
                col, rem = divmod(col - 1, 26)
                letters = chr(65 + rem) + letters
            return f"{letters}{row}"

        def value_cell(row: int, col: int, value: object) -> str:
            ref = cell_ref(row, col)
            if isinstance(value, (int, float)):
                return f'<c r="{ref}"><v>{value}</v></c>'
            text = html.escape("" if value is None else str(value))
            return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'

        rows: list[list[object]] = [
            [f"Рейсы: {shipment_date if shipment_date else 'все даты'}"],
            [],
            ["Дата", "#", "Пал.", "Вес кг", "Объём м³", "Тип ТС", "Машина", "Водитель", "ДОК", "Регионы", "Цена ₽", "ТК", "Логист", "Статус"],
        ]
        for task in tasks:
            rows.append([
                str(task.get("SHIPMENT_DATE") or "")[:10],
                task.get("ID"),
                task.get("PALLET_COUNT"),
                task.get("TEMP_WEIGHT"),
                task.get("VOLUME_M3"),
                task.get("TRANSTYPE"),
                task.get("TRANSPORT"),
                task.get("VODITEL_NAME"),
                task.get("DOCK"),
                task.get("REGIONS") or task.get("TEMP_REGION"),
                float(task.get("PRICE") or 0),
                task.get("TK_NAME"),
                task.get("LOGIST"),
                task.get("CONDITION"),
            ])

        sheet_rows = []
        for row_idx, row in enumerate(rows, start=1):
            cells = "".join(value_cell(row_idx, col_idx, value) for col_idx, value in enumerate(row, start=1))
            sheet_rows.append(f'<row r="{row_idx}">{cells}</row>')
        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            + "".join(sheet_rows)
            + '</sheetData></worksheet>'
        )
        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Рейсы" sheetId="1" r:id="rId1"/></sheets></workbook>'
        )
        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'
        )
        root_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", root_rels)
            archive.writestr("xl/workbook.xml", workbook_xml)
            archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        return buf.getvalue()

    def get_plan_fact(self, date_from: date, date_to: date, vehicle: str | None = None) -> list[dict]:
        """Сводный план-фактный отчёт по всем рейсам периода."""
        params: dict[str, Any] = {
            "d_from": str(date_from),
            "d_to": str(date_to),
        }
        vehicle_clause = ""
        if vehicle:
            vehicle_clause = "AND TT.TRANSPORT = :vehicle"
            params["vehicle"] = vehicle

        tasks = self.gateway.fetch_all(
            f"""
            SELECT TT.ID AS TT_ID,
                   TT.TRANSPORT AS VEHICLE,
                   TO_CHAR(TT.SHIPMENT_DATE, 'YYYY-MM-DD') AS SHIPMENT_DATE,
                   TT.CONDITION AS STATUS
              FROM RABAEV.RRL_TRANSPORT_TASK TT
             WHERE TT.SHIPMENT_DATE >= TO_DATE(:d_from, 'YYYY-MM-DD')
               AND TT.SHIPMENT_DATE <  TO_DATE(:d_to,   'YYYY-MM-DD') + 1
               AND NVL(TT.DELETED, 0) = 0
               {vehicle_clause}
             ORDER BY TT.SHIPMENT_DATE, TT.TRANSPORT
            """,
            params,
        )

        result = []
        for t in tasks:
            ops = self.get_operations(int(t["TT_ID"]))
            total_delta = sum(
                abs(op["delta_min"]) for op in ops if op["delta_min"] is not None
            )
            # Count rest violations: DRIVE + DRIVE_BACK total > 540 min (9 h)
            drive_min = sum(
                op["duration_min"]
                for op in ops
                if op["operation_code"] in ("DRIVE", "DRIVE_BACK")
            )
            rest_violations = 1 if drive_min > 540 else 0

            result.append(
                {
                    "tt_id": int(t["TT_ID"]),
                    "vehicle": t.get("VEHICLE") or "",
                    "shipment_date": t.get("SHIPMENT_DATE") or "",
                    "status": t.get("STATUS") or "",
                    "operations": ops,
                    "total_delta_min": round(total_delta, 1),
                    "rest_violations": rest_violations,
                }
            )
        return result
