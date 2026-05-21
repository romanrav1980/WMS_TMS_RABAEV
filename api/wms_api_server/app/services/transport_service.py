"""
transport_service.py — Сервис диспетчера отгрузки, Фаза 1: ручное назначение.

Все мутации данных выполняются через существующие Oracle-функции:
  RRL_TRASPORT_TASK_ADD  — создать рейс
  RRL_TT_ADD_PALL        — назначить / снять СТ (tt_id=0 → снять)
  RRL_TT_REORDER_ADR     — пересортировать СТ в рейсе по ORD адреса

Чтение — напрямую через SELECT / представление RRL_V_AVAILABLE_STS.
"""

from datetime import date
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import TransportTaskCreateRequest, TransportTaskUpdateRequest


class TransportService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    # ------------------------------------------------------------------
    # Справочники
    # ------------------------------------------------------------------

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
                   F, I, O, TEL, TRANSPORT_NUM, SOBSTVENNYY
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
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if not include_deleted:
            conditions.append("(TT.DELETED IS NULL OR TT.DELETED = 0)")
        if shipment_date is not None:
            conditions.append("TRUNC(TT.SHIPMENT_DATE) = :shipment_date")
            params["shipment_date"] = shipment_date
        if condition:
            conditions.append("TT.CONDITION = :condition")
            params["condition"] = condition

        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""

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
                   TT.PRIMECHANIE,
                   TT.DOCK,
                   TT.SHIPMENT_TIME,
                   TT.TEMP_REGION,
                   TT.TEMP_WEIGHT,
                   TT.PRICE,
                   TT.DELETED,
                   COUNT(SP.ID)                           AS PALLET_COUNT,
                   COUNT(DISTINCT SP.ST_NUMBER)           AS ST_COUNT
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TR_VODITEL V ON V.ID = TT.VODITEL_ID
              LEFT JOIN RABAEV.RRL_SBORKA_PALLETS SP
                ON SP.TRANSTASK_ID = TT.ID
               AND (SP.DELETED IS NULL OR SP.DELETED <> 1)
              {where_sql}
             GROUP BY TT.ID, TT.CREATEDATE, TT.TRANSPORT, TT.TRANSTYPE,
                      TT.CONDITION, TT.SHIPMENT_DATE, TT.PLANNED_DELIVERY_DATE,
                      TT.VODITEL_ID, V.F, V.I, V.O, V.TEL,
                      TT.PRIMECHANIE, TT.DOCK, TT.SHIPMENT_TIME,
                      TT.TEMP_REGION, TT.TEMP_WEIGHT, TT.PRICE, TT.DELETED
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

        if not sets:
            return

        self.gateway.execute(
            f"UPDATE RABAEV.RRL_TRANSPORT_TASK SET {', '.join(sets)} WHERE ID = :task_id",
            params,
        )

    def close_task(self, task_id: int, user_id: str) -> None:
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
                   NVL(A.REGION, SP.ADDR)           AS REGION,
                   A.RAION,
                   SP.ORD,
                   COUNT(DISTINCT SP.PALLET_UID)     AS PALLETS_COUNT,
                   ROUND(SUM(NVL(R.ORDER_WEIGHT,0)),0) AS WEIGHT_KG,
                   MAX(SP.STDATE)                    AS STDATE
              FROM RABAEV.RRL_SBORKA_PALLETS SP
              JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = SP.PALLET_UID
              LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
             WHERE SP.TRANSTASK_ID = :task_id
               AND (SP.DELETED IS NULL OR SP.DELETED <> 1)
             GROUP BY SP.ST_NUMBER, SP.ADDR, A.REGION, A.RAION, SP.ORD
             ORDER BY SP.ORD NULLS LAST, SP.ST_NUMBER
            """,
            {"task_id": task_id},
        )

    def assign_sts(self, task_id: int, st_numbers: list[str], user_id: str) -> dict[str, Any]:
        warnings: list[str] = []

        # Проверить, не назначены ли уже СТ на другой рейс
        for st in st_numbers:
            rows = self.gateway.fetch_all(
                """
                SELECT DISTINCT TRANSTASK_ID
                  FROM RABAEV.RRL_SBORKA_PALLETS
                 WHERE ST_NUMBER = :st
                   AND TRANSTASK_ID IS NOT NULL
                   AND TRANSTASK_ID <> :task_id
                   AND (DELETED IS NULL OR DELETED <> 1)
                   AND ROWNUM = 1
                """,
                {"st": st, "task_id": task_id},
            )
            if rows:
                other_id = rows[0]["TRANSTASK_ID"]
                warnings.append(f"СТ {st} уже назначено на рейс #{other_id}")

        # Назначить каждое СТ через Oracle-функцию
        for st in st_numbers:
            self.gateway.call_varchar_function(
                "RABAEV.RRL_TT_ADD_PALL",
                {"TT_ID": task_id, "ST_NUMBER1": st},
            )

        # Пересортировать по адресному порядку (обновляет также PRICE)
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

    # ------------------------------------------------------------------
    # Свободные СТ
    # ------------------------------------------------------------------

    def list_available_sts(
        self,
        stdate: date | None = None,
        unassigned_only: bool = True,
        ware_id: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if unassigned_only:
            conditions.append("TRANSTASK_ID IS NULL")
        if stdate is not None:
            conditions.append("TRUNC(STDATE) = :stdate")
            params["stdate"] = stdate
        if ware_id is not None:
            conditions.append("WARE_ID = :ware_id")
            params["ware_id"] = ware_id

        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""

        return self.gateway.fetch_all(
            f"""
            SELECT ST_NUMBER, ADDR, REGION, RAION, ORD,
                   TRANSPORT_TYPE, NEEDS_HYDRO_BOARD,
                   WARE_ID, PALLETS_COUNT, WEIGHT_KG, VOLUME_M3,
                   STDATE, TRANSTASK_ID
              FROM RABAEV.RRL_V_AVAILABLE_STS
              {where_sql}
             ORDER BY ORD NULLS LAST, REGION, ST_NUMBER
            """,
            params,
        )
