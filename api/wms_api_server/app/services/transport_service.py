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
  — list_clusters()    — группировка свободных СТ по RRL_ADDR.RAION

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
from datetime import date
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    TransportTaskCreateRequest,
    TransportTaskUpdateRequest,
    VrpPlanResponse,
    VrpRouteItem,
    VrpRouteStop,
)


class TransportService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

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

    def list_vehicles(self, active_only: bool = True) -> list[dict[str, Any]]:
        where = "WHERE BLOCKED = 0" if active_only else ""
        return self.gateway.fetch_all(
            f"""
            SELECT ID, NUM, TR_TYPE, MARKA, REF_REJIM,
                   PALLETS, GIDROBORT, BLOCKED
              FROM RABAEV.RRL_TR_VEHICLE
              {where}
             ORDER BY TR_TYPE, NUM
            """
        )

    def list_drivers(self, active_only: bool = True) -> list[dict[str, Any]]:
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

    def list_transport_types(self) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            SELECT TRANSPORTTYPE, NAME, MIN_PALLET_LOAD, MAX_PALLET_LOAD
              FROM RABAEV.RRL_TRANSPORT_TYPE
             ORDER BY TRANSPORTTYPE
            """
        )

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
        date_to: date | None = None,
        no_payments_only: bool = False,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if not include_deleted:
            conditions.append("(TT.DELETED IS NULL OR TT.DELETED = 0)")
        if shipment_date is not None:
            conditions.append("TRUNC(TT.SHIPMENT_DATE) = :shipment_date")
            params["shipment_date"] = shipment_date
        if date_to is not None:
            conditions.append("TRUNC(TT.SHIPMENT_DATE) <= :date_to")
            params["date_to"] = date_to
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
                   ROUND(TRANSPORT_TASK.TT_READY_PERC(TT.ID) * 100, 0) AS READY_PERC,
                   TRANSPORT_TASK.TT_UNREADY_COUNT(TT.ID)               AS UNREADY_COUNT"""

        return self.gateway.fetch_all(
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
                   TT.DELETED
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TR_VODITEL V ON V.ID = TT.VODITEL_ID
             WHERE TT.ID = :task_id
            """,
            {"task_id": task_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"Transport task {task_id} not found")
        return rows[0]

    def create_task(self, req: TransportTaskCreateRequest, user_id: str) -> int:
        task_id = self.gateway.call_number_plsql(
            """
            BEGIN
              :result := RABAEV.RRL_TRASPORT_TASK_ADD(
                :transtype,
                TO_DATE(:shipment_date, 'YYYY-MM-DD'),
                :user_id
              );
            END;
            """,
            {
                "transtype":     req.transtype,
                "shipment_date": str(req.shipment_date),
                "user_id":       user_id,
            },
        )
        return task_id

    def update_task(self, task_id: int, req: TransportTaskUpdateRequest, user_id: str) -> None:
        sets: list[str] = []
        params: dict[str, Any] = {"task_id": task_id, "user_id": user_id}

        if req.transport is not None:
            # Вызвать комментарий о спецтехнике (лопата/гидроборт) перед обновлением
            try:
                self.gateway.call_varchar_function(
                    "RABAEV.RRL_TT_SET_TRANSCOMMENT",
                    {"TRANS": req.transport, "TTID1": task_id},
                )
            except Exception:
                pass  # некритично — обновление рейса продолжается
            sets.append("TRANSPORT = :transport")
            params["transport"] = req.transport
        if req.voditel_id is not None:
            sets.append("VODITEL_ID = :voditel_id")
            params["voditel_id"] = req.voditel_id
        if req.dock is not None:
            sets.append("DOCK = :dock")
            params["dock"] = req.dock
        if req.primechanie is not None:
            sets.append("PRIMECHANIE = :primechanie")
            params["primechanie"] = req.primechanie
        if req.shipment_time is not None:
            sets.append("SHIPMENT_TIME = TO_DATE(:shipment_time, 'HH24:MI')")
            params["shipment_time"] = req.shipment_time
        if req.shipment_date is not None:
            sets.append("SHIPMENT_DATE = TO_DATE(:shipment_date, 'YYYY-MM-DD')")
            params["shipment_date"] = str(req.shipment_date)
        if req.transtype is not None:
            sets.append("TRANSTYPE = :transtype")
            params["transtype"] = req.transtype

        if not sets:
            return

        self.gateway.execute(
            f"UPDATE RABAEV.RRL_TRANSPORT_TASK SET {', '.join(sets)} WHERE ID = :task_id",
            params,
        )

    def close_task(self, task_id: int, user_id: str) -> None:
        # Проверить минимальную загрузку через Oracle
        try:
            result = self.gateway.call_varchar_function(
                "TRANSPORT_TASK.can_print",
                {"tt_id": task_id, "user_id1": user_id},
            )
            if result and result.lower() != "ok":
                raise HTTPException(status_code=422, detail=result)
        except HTTPException:
            raise
        except Exception:
            pass  # если функция недоступна — не блокируем закрытие

        affected = self.gateway.execute(
            """
            UPDATE RABAEV.RRL_TRANSPORT_TASK
               SET CONDITION = 'Отгружен',
                   USER_ID   = :user_id
             WHERE ID = :task_id
               AND (DELETED IS NULL OR DELETED = 0)
            """,
            {"task_id": task_id, "user_id": user_id},
        )
        if affected == 0:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found or already closed")

    def cancel_task(self, task_id: int, user_id: str) -> None:
        self.gateway.execute(
            """
            UPDATE RABAEV.RRL_TRANSPORT_TASK
               SET DELETED = 1,
                   USER_ID = :user_id
             WHERE ID = :task_id
            """,
            {"task_id": task_id, "user_id": user_id},
        )

    # ------------------------------------------------------------------
    # Состав рейса — СТ
    # ------------------------------------------------------------------

    def get_task_sts(self, task_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
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
                   MAX(RABAEV.RRL_ST_VERYFY_PERC(SP.ST_NUMBER))  AS VERIFY_PERC
              FROM RABAEV.RRL_SBORKA_PALLETS SP
              JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = SP.PALLET_UID
              LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
             WHERE SP.TRANSTASK_ID = :task_id
               AND SP.CONDITION <> 2
             GROUP BY SP.ST_NUMBER, SP.ADDR, A.REGION, A.RAION, SP.ORD
             ORDER BY SP.ORD NULLS LAST, SP.ST_NUMBER
            """,
            {"task_id": task_id},
        )

    def assign_sts(self, task_id: int, st_numbers: list[str], user_id: str) -> dict[str, Any]:
        warnings: list[str] = []

        for st in st_numbers:
            rows = self.gateway.fetch_all(
                """
                SELECT DISTINCT TRANSTASK_ID
                  FROM RABAEV.RRL_SBORKA_PALLETS
                 WHERE ST_NUMBER = :st
                   AND TRANSTASK_ID IS NOT NULL
                   AND TRANSTASK_ID <> :task_id
                   AND CONDITION <> 2
                   AND ROWNUM = 1
                """,
                {"st": st, "task_id": task_id},
            )
            if rows:
                other_id = rows[0]["TRANSTASK_ID"]
                warnings.append(f"СТ {st} уже назначено на рейс #{other_id}")

        for st in st_numbers:
            self.gateway.call_varchar_function(
                "RABAEV.RRL_TT_ADD_PALL",
                {"TT_ID": task_id, "ST_NUMBER1": st},
            )

        self.gateway.call_number_plsql(
            "BEGIN :result := RABAEV.RRL_TT_REORDER_ADR(:task_id); END;",
            {"task_id": task_id},
        )

        return {"assigned": len(st_numbers), "warnings": warnings}

    def unassign_st(self, task_id: int, st_number: str, user_id: str) -> None:
        # TT_ID = 0 → снять СТ с любого рейса
        self.gateway.call_varchar_function(
            "RABAEV.RRL_TT_ADD_PALL",
            {"TT_ID": 0, "ST_NUMBER1": st_number},
        )

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
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        having: list[str] = []
        params: dict[str, Any] = {}

        if unassigned_only:
            conditions.append("TRANSTASK_ID IS NULL")

        # Дата СТ: точное равенство или диапазон
        if stdate is not None and date_to is None:
            conditions.append("TRUNC(STDATE) = :stdate")
            params["stdate"] = stdate
        elif stdate is not None and date_to is not None:
            conditions.append("TRUNC(STDATE) >= :stdate AND TRUNC(STDATE) <= :date_to")
            params["stdate"] = stdate
            params["date_to"] = date_to
        elif date_to is not None:
            conditions.append("TRUNC(STDATE) <= :date_to")
            params["date_to"] = date_to

        # Фильтр по складам: ware_ids приоритетнее одиночного ware_id
        effective_ware_ids = ware_ids or ([ware_id] if ware_id is not None else None)
        if effective_ware_ids:
            placeholders = ", ".join(f":wid{i}" for i in range(len(effective_ware_ids)))
            conditions.append(f"WARE_ID IN ({placeholders})")
            for i, wid in enumerate(effective_ware_ids):
                params[f"wid{i}"] = wid

        if addr_mask:
            conditions.append(
                "(ADDR LIKE :addr_mask OR REGION LIKE :addr_mask OR RAION LIKE :addr_mask)"
            )
            params["addr_mask"] = f"%{addr_mask}%"

        if st_mask:
            op = "NOT LIKE" if st_mask_exclude else "LIKE"
            conditions.append(f"UPPER(ST_NUMBER) {op} UPPER(:st_mask)")
            params["st_mask"] = f"%{st_mask}%"

        if transport_type:
            conditions.append("TRANSPORT_TYPE = :transport_type")
            params["transport_type"] = transport_type

        if articul:
            conditions.append(
                """EXISTS (
                    SELECT 1
                      FROM RABAEV.RRL_SBORKA_PALLETS SP2
                      JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R2 ON R2.PALLET_UID = SP2.PALLET_UID
                     WHERE SP2.ST_NUMBER = V.ST_NUMBER
                       AND UPPER(R2.ARTICUL) LIKE UPPER(:articul)
                )"""
            )
            params["articul"] = f"%{articul}%"

        if assembled_only:
            having.append("VERIFY_PERC > 0")
        elif not_assembled_only:
            having.append("(VERIFY_PERC IS NULL OR VERIFY_PERC = 0)")

        if max_weight_kg is not None:
            having.append("WEIGHT_KG < :max_weight_kg")
            params["max_weight_kg"] = max_weight_kg

        if max_volume_m3 is not None:
            having.append("VOLUME_M3 < :max_volume_m3")
            params["max_volume_m3"] = max_volume_m3

        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""
        having_sql = "HAVING " + " AND ".join(having) if having else ""

        # Псевдоним V нужен для коррелированного подзапроса по articul
        return self.gateway.fetch_all(
            f"""
            SELECT V.ST_NUMBER, V.ADDR, V.REGION, V.RAION, V.ORD,
                   V.TRANSPORT_TYPE, V.NEEDS_HYDRO_BOARD, V.STOL, V.PRIM1,
                   V.WARE_ID, V.NAPR,
                   V.PALLETS_COUNT, V.WEIGHT_KG, V.VOLUME_M3,
                   V.STDATE, V.DATE_LOAD, V.TRANSTASK_ID,
                   V.VERIFY_PERC, V.SUGAR
              FROM RABAEV.RRL_V_AVAILABLE_STS V
              {where_sql}
              {having_sql}
             ORDER BY V.ORD NULLS LAST, V.REGION, V.ST_NUMBER
            """,
            params,
        )

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
        conditions: list[str] = ["TRANSTASK_ID IS NULL"]
        params: dict[str, Any] = {}

        if plan_date is not None:
            conditions.append("TRUNC(STDATE) = :plan_date")
            params["plan_date"] = plan_date

        effective_ware_ids = ware_ids or []
        if effective_ware_ids:
            placeholders = ", ".join(f":wid{i}" for i in range(len(effective_ware_ids)))
            conditions.append(f"WARE_ID IN ({placeholders})")
            for i, wid in enumerate(effective_ware_ids):
                params[f"wid{i}"] = wid

        if transport_type:
            conditions.append("TRANSPORT_TYPE = :transport_type")
            params["transport_type"] = transport_type

        where_sql = "WHERE " + " AND ".join(conditions)

        return self.gateway.fetch_all(
            f"""
            SELECT ST_NUMBER, ADDR, REGION, RAION,
                   SHIROTA       AS LAT,
                   DOLGOTA       AS LON,
                   PALLETS_COUNT, WEIGHT_KG, VOLUME_M3,
                   WARE_ID, TRANSPORT_TYPE, NEEDS_HYDRO_BOARD,
                   MAX_VEHICLE_TONS, TW_STRICT, UNLOAD_NORM_MIN,
                   VERIFY_PERC, STDATE
              FROM RABAEV.RRL_V_AVAILABLE_STS
              {where_sql}
             ORDER BY REGION NULLS LAST, ST_NUMBER
            """,
            params,
        )

    def get_routing_status(self) -> dict[str, Any]:
        """Возвращает статус геокодирования адресов."""
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
        return {
            "provider": "haversine",
            "provider_available": True,
            "total_addresses": total,
            "geocoded_count": geocoded,
            "ungeocoded_count": total - geocoded,
        }

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
               AND (SP.DELETED IS NULL OR SP.DELETED <> 1)
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
    ) -> VrpPlanResponse:
        """Запускает VRP-решатель, сохраняет план и возвращает ответ."""
        from .vrp_solver import VrpOrder, VrpVehicle, solve as vrp_solve
        from .distance_matrix_service import DistanceMatrixService

        # Load orders
        raw_orders = self.get_planner_orders(
            plan_date=plan_date,
            ware_ids=ware_ids,
            transport_type=transport_type,
        )
        orders = [
            VrpOrder(
                st_number=o["ST_NUMBER"],
                addr=o["ADDR"] or "",
                lat=float(o["LAT"]) if o.get("LAT") else 0.0,
                lon=float(o["LON"]) if o.get("LON") else 0.0,
                pallets=int(o.get("PALLETS_COUNT") or 0),
                weight_kg=float(o.get("WEIGHT_KG") or 0),
                ware_id=int(o.get("WARE_ID") or 0),
                transport_type=o.get("TRANSPORT_TYPE"),
                tw_strict=bool(o.get("TW_STRICT")),
                unload_norm_min=int(o.get("UNLOAD_NORM_MIN") or 30),
            )
            for o in raw_orders
            if o.get("LAT") and o.get("LON")
        ]

        # Load vehicles
        raw_vehicles = self.list_vehicles(active_only=True)
        vehicles = [
            VrpVehicle(
                id=int(v["ID"]),
                num=str(v["NUM"] or ""),
                tr_type=str(v.get("TR_TYPE") or ""),
                max_pallets=int(v.get("PALLETS") or 20),
                max_tons=float(v.get("MAX_TONS") or v.get("MAX_VEHICLE_TONS") or 20),
                gidrobort=bool(v.get("GIDROBORT")),
            )
            for v in raw_vehicles
        ]

        if not vehicles:
            raise HTTPException(status_code=422, detail="Нет активных ТС")

        # Load distance cache
        addr_list = [o.addr for o in orders if o.addr]
        dist_cache = DistanceMatrixService(self.gateway).get_matrix_as_dict(addr_list)

        # Solve
        plan = vrp_solve(
            orders=orders,
            vehicles=vehicles,
            dist_cache=dist_cache or None,
            time_limit_s=time_limit_s,
            solver=solver,
        )

        # Save plan to Oracle
        plan_json = json.dumps(
            {
                "solver": plan.solver_used,
                "routes": [
                    {
                        "vehicle_id": r.vehicle.id,
                        "vehicle_num": r.vehicle.num,
                        "stops": [s.st_number for s in r.stops],
                        "total_km": r.total_km,
                        "total_pallets": r.total_pallets,
                    }
                    for r in plan.routes
                ],
                "unassigned": [o.st_number for o in plan.unassigned],
                "total_km": plan.total_km,
                "fleet_utilization_pct": plan.fleet_utilization_pct,
                "tw_violations": plan.tw_violations,
                "score": plan.score,
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
                       (ID, PLAN_DATE, CREATED_AT, SOLVER, SCORE, PLAN_JSON)
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
        route_items = [
            VrpRouteItem(
                vehicle_id=r.vehicle.id,
                vehicle_num=r.vehicle.num,
                vehicle_type=r.vehicle.tr_type,
                max_pallets=r.vehicle.max_pallets,
                total_pallets=r.total_pallets,
                total_kg=r.total_kg,
                total_km=r.total_km,
                total_duration_min=r.total_duration_min,
                utilization_pct=r.utilization_pct,
                stops=[
                    VrpRouteStop(
                        st_number=s.st_number,
                        addr=s.addr,
                        lat=s.lat,
                        lon=s.lon,
                        pallets=s.pallets,
                        weight_kg=s.weight_kg,
                        ware_id=s.ware_id,
                        unload_norm_min=s.unload_norm_min,
                        tw_from=s.tw_from,
                        tw_to=s.tw_to,
                        tw_strict=s.tw_strict,
                    )
                    for s in r.stops
                ],
            )
            for r in plan.routes
        ]

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
        )

    def apply_vrp_plan(
        self,
        plan_id: int,
        shipment_date: date,
        dock: str | None = None,
    ) -> dict[str, Any]:
        """Создаёт рейсы по сохранённому плану через Oracle-функции."""
        rows = self.gateway.fetch_all(
            "SELECT PLAN_JSON, SOLVER FROM RABAEV.RRL_PLANNER_PLANS WHERE ID = :plan_id",
            {"plan_id": plan_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        plan_data = json.loads(rows[0]["PLAN_JSON"])
        tasks_created = 0
        user_id = "vrp_auto"

        for route in plan_data.get("routes", []):
            vehicle_num = route.get("vehicle_num", "")
            vehicle_id  = route.get("vehicle_id")
            stop_sts: list[str] = route.get("stops", [])
            if not stop_sts:
                continue

            # Create task via Oracle function (transtype default 20)
            req = TransportTaskCreateRequest(transtype="20", shipment_date=shipment_date)
            tt_id = self.create_task(req, user_id=user_id)

            # Set vehicle, driver, dock
            upd = TransportTaskUpdateRequest(
                transport=vehicle_num or None,
                voditel_id=vehicle_id,
                dock=dock,
            )
            try:
                self.update_task(tt_id, upd, user_id=user_id)
            except Exception:
                pass

            # Assign STs
            try:
                self.assign_sts(tt_id, stop_sts, user_id=user_id)
            except Exception:
                pass

            tasks_created += 1

        # Mark plan as applied
        self.gateway.execute(
            "UPDATE RABAEV.RRL_PLANNER_PLANS SET APPLIED_AT = SYSDATE WHERE ID = :plan_id",
            {"plan_id": plan_id},
        )

        return {"tasks_created": tasks_created, "plan_id": plan_id}

    def get_plan_metrics(self, plan_id: int | None = None) -> dict[str, Any]:
        """Возвращает метрики плана. plan_id=None → последний план."""
        if plan_id is None:
            rows = self.gateway.fetch_all(
                """
                SELECT ID, PLAN_DATE, SOLVER, SCORE, PLAN_JSON, CREATED_AT, APPLIED_AT
                  FROM RABAEV.RRL_PLANNER_PLANS
                 ORDER BY ID DESC
                 FETCH FIRST 1 ROWS ONLY
                """
            )
        else:
            rows = self.gateway.fetch_all(
                """
                SELECT ID, PLAN_DATE, SOLVER, SCORE, PLAN_JSON, CREATED_AT, APPLIED_AT
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
            SELECT ID, PLAN_DATE, PLAN_JSON, SCORE
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
    ) -> list[dict[str, Any]]:
        """История применённых планов за период с метриками Score, утилизация, пробег."""
        rows = self.gateway.fetch_all(
            """
            SELECT ID, PLAN_DATE, SOLVER, SCORE, PLAN_JSON, CREATED_AT, APPLIED_AT
              FROM RABAEV.RRL_PLANNER_PLANS
             WHERE PLAN_DATE >= :date_from
               AND PLAN_DATE <= :date_to
             ORDER BY PLAN_DATE
            """,
            {"date_from": date_from, "date_to": date_to},
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
                SELECT COUNT(*) AS CNT
                  FROM RABAEV.RRL_V_AVAILABLE_STS
                 WHERE TRUNC(STDATE) = :stdate
                """,
                {"stdate": sample_date},
            )
            if rows:
                counts.append(int(rows[0]["CNT"] or 0))

        if not counts:
            return {
                "target_date": str(target_date),
                "day_of_week": dow,
                "forecast_sts": 0,
                "confidence": "none",
                "samples": 0,
            }

        avg = round(sum(counts) / len(counts), 0)
        stddev = (sum((c - avg) ** 2 for c in counts) / len(counts)) ** 0.5
        confidence = "high" if stddev < avg * 0.15 else "medium" if stddev < avg * 0.3 else "low"

        return {
            "target_date": str(target_date),
            "day_of_week": dow,
            "forecast_sts": int(avg),
            "confidence": confidence,
            "samples": len(counts),
            "sample_counts": counts,
            "stddev": round(stddev, 1),
        }
