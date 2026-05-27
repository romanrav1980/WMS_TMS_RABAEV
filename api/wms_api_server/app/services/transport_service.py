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
from datetime import date
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    OperationFactUpdate,
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

    def create_task_from_cluster(
        self,
        raion: str,
        req: "ClusterCreateTaskRequest",
        user_id: str,
    ) -> dict[str, Any]:
        """Создаёт рейс из всех свободных СТ района одним запросом (Sprint 29, Phase 2).

        Последовательность:
          1. list_available_sts → фильтр по raion
          2. RRL_TRASPORT_TASK_ADD  — создать рейс
          3. UPDATE TRANSPORT/VODITEL/DOCK (если переданы)
          4. RRL_TT_ADD_PALL × N   — назначить все СТ
          5. RRL_TT_REORDER_ADR    — оптимизировать порядок
        """
        # 1. Собрать свободные СТ района — server-side raion filter (Sprint 35)
        sts = self.list_available_sts(
            stdate=req.stdate,
            unassigned_only=True,
            ware_ids=req.ware_ids,
            raion=raion,
        )
        if not sts:
            raise HTTPException(
                status_code=404,
                detail=f"Нет свободных СТ в районе «{raion}» на {req.stdate}",
            )

        # 2. Создать рейс
        from ..schemas import TransportTaskCreateRequest as _TtCreate, TransportTaskUpdateRequest as _TtUpd
        task_id = self.create_task(
            _TtCreate(transtype=req.transtype, shipment_date=req.stdate),
            user_id,
        )

        # 3. Назначить машину/водителя/докст. (если переданы)
        if req.vehicle or req.driver_id or req.dock:
            self.update_task(
                task_id,
                _TtUpd(transport=req.vehicle, voditel_id=req.driver_id, dock=req.dock),
                user_id,
            )

        # 4–5. Назначить СТ + оптимизировать порядок
        st_numbers = [str(s["ST_NUMBER"]) for s in sts]
        result = self.assign_sts(task_id, st_numbers, user_id)

        return {
            "task_id": task_id,
            "raion": raion,
            "st_count": len(st_numbers),
            "warnings": result.get("warnings", []),
        }

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
        task = self.get_task(task_id)
        if task and task.get("PAY_ORDER_ID"):
            raise HTTPException(
                status_code=409,
                detail=f"Рейс включён в счёт №{task['PAY_ORDER_ID']} — расформирование запрещено",
            )
        # Unassign all STs first so they become available for new trips.
        # RRL_TT_ADD_PALL(TT_ID=0) detaches an ST from any task.
        sts = self.get_task_sts(task_id)
        for st in sts:
            self.gateway.call_varchar_function(
                "RABAEV.RRL_TT_ADD_PALL",
                {"TT_ID": 0, "ST_NUMBER1": st["ST_NUMBER"]},
            )
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
        task = self.get_task(task_id)
        if task and task.get("PAY_ORDER_ID"):
            raise HTTPException(
                status_code=409,
                detail=f"Рейс включён в счёт №{task['PAY_ORDER_ID']} — добавление СТ запрещено",
            )
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
        task = self.get_task(task_id)
        if task and task.get("PAY_ORDER_ID"):
            raise HTTPException(
                status_code=409,
                detail=f"Рейс включён в счёт №{task['PAY_ORDER_ID']} — снятие СТ запрещено",
            )
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
        raion: str | None = None,
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

        if raion is not None:
            if raion == "(без района)":
                conditions.append("RAION IS NULL")
            else:
                conditions.append("RAION = :raion")
                params["raion"] = raion

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

    # ------------------------------------------------------------------
    # Sprint 11 — ARM: операции и нормативы
    # ------------------------------------------------------------------

    def _load_norms(self) -> dict[str, dict]:
        """Загружает нормативы из RRL_TRANSPORT_NORMS → {code: {dur, per_unit}}."""
        rows = self.gateway.fetch_all(
            "SELECT OPERATION_CODE, DURATION_MIN, PER_UNIT FROM RABAEV.RRL_TRANSPORT_NORMS"
        )
        return {
            r["OPERATION_CODE"]: {
                "duration_min": float(r["DURATION_MIN"]),
                "per_unit": int(r["PER_UNIT"] or 0),
            }
            for r in rows
        }

    def plan_operations(self, task_id: int) -> list[dict]:
        """Рассчитывает и сохраняет цепочку плановых операций рейса.

        Цепочка: DOCK_ASSIGN → WAIT_LOAD → LOADING → CLOSE_GATE → DOCUMENTS →
                 DEPART → DRIVE → UNLOAD → LOAD_RETURNS → DRIVE_BACK →
                 RETURN_HANDOVER → CLEAN_RETURNS
        Начальная точка отсчёта — SHIPMENT_TIME рейса (или 06:00 если не задано).
        """
        from datetime import datetime, timedelta

        # Загрузить рейс
        task = self.get_task(task_id)

        # Определить начальное время
        raw_time = task.get("SHIPMENT_TIME")
        if raw_time:
            # SHIPMENT_TIME может прийти как datetime или строка
            if isinstance(raw_time, datetime):
                start_dt = raw_time
            else:
                try:
                    start_dt = datetime.strptime(str(raw_time)[:16], "%Y-%m-%d %H:%M")
                except ValueError:
                    plan_date = task.get("SHIPMENT_DATE") or datetime.today()
                    if not isinstance(plan_date, datetime):
                        plan_date = datetime.combine(plan_date, datetime.min.time())
                    start_dt = plan_date.replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            plan_date = task.get("SHIPMENT_DATE")
            if plan_date:
                if isinstance(plan_date, datetime):
                    start_dt = plan_date.replace(hour=6, minute=0, second=0, microsecond=0)
                else:
                    from datetime import date as date_cls
                    if isinstance(plan_date, date_cls):
                        start_dt = datetime.combine(plan_date, datetime.min.time()).replace(hour=6)
                    else:
                        start_dt = datetime.today().replace(hour=6, minute=0, second=0, microsecond=0)
            else:
                start_dt = datetime.today().replace(hour=6, minute=0, second=0, microsecond=0)

        # Суммарные паллеты рейса
        sts = self.get_task_sts(task_id)
        total_pallets = sum(int(s.get("PALLETS_COUNT") or 0) for s in sts)
        if total_pallets <= 0:
            total_pallets = 1  # минимум 1, чтобы LOADING/UNLOAD не были 0

        norms = self._load_norms()

        # Порядок операций в цепочке
        CHAIN = [
            "DOCK_ASSIGN", "WAIT_LOAD", "LOADING", "CLOSE_GATE", "DOCUMENTS",
            "DEPART", "DRIVE", "UNLOAD", "LOAD_RETURNS", "DRIVE_BACK",
            "RETURN_HANDOVER", "CLEAN_RETURNS",
        ]

        # Удалить старые операции этого рейса
        self.gateway.execute(
            "DELETE FROM RABAEV.RRL_TT_OPERATIONS WHERE TT_ID = :tt_id",
            {"tt_id": task_id},
        )

        result = []
        current_dt = start_dt
        for ord_num, code in enumerate(CHAIN, start=1):
            norm = norms.get(code, {"duration_min": 0.0, "per_unit": 0})
            dur = norm["duration_min"]
            if norm["per_unit"]:
                dur = dur * total_pallets

            plan_start = current_dt
            plan_end = current_dt + timedelta(minutes=dur)

            # INSERT нового шага
            rows = self.gateway.fetch_all(
                "SELECT RABAEV.SEQ_TT_OPERATIONS.NEXTVAL AS NV FROM DUAL"
            )
            op_id = int(rows[0]["NV"])

            self.gateway.execute(
                """
                INSERT INTO RABAEV.RRL_TT_OPERATIONS
                  (ID, TT_ID, OPERATION_CODE, ORD, DURATION_MIN, PLAN_START, PLAN_END)
                VALUES
                  (:id, :tt_id, :code, :ord, :dur,
                   TO_DATE(:ps, 'YYYY-MM-DD HH24:MI'), TO_DATE(:pe, 'YYYY-MM-DD HH24:MI'))
                """,
                {
                    "id": op_id,
                    "tt_id": task_id,
                    "code": code,
                    "ord": ord_num,
                    "dur": round(dur, 2),
                    "ps": plan_start.strftime("%Y-%m-%d %H:%M"),
                    "pe": plan_end.strftime("%Y-%m-%d %H:%M"),
                },
            )

            result.append(
                {
                    "op_id": op_id,
                    "tt_id": task_id,
                    "operation_code": code,
                    "ord": ord_num,
                    "duration_min": round(dur, 2),
                    "plan_start": plan_start.strftime("%Y-%m-%d %H:%M"),
                    "plan_end": plan_end.strftime("%Y-%m-%d %H:%M"),
                    "fact_start": None,
                    "fact_end": None,
                    "delta_min": None,
                    "note": None,
                }
            )

            current_dt = plan_end

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

        from datetime import datetime as dt

        def _parse(s):
            return dt.strptime(s, "%Y-%m-%d %H:%M") if s else None

        result = []
        for r in rows:
            delta = None
            if r["FACT_END"] and r["PLAN_END"]:
                delta = round(
                    (_parse(r["FACT_END"]) - _parse(r["PLAN_END"])).total_seconds() / 60, 1
                )
            result.append(
                {
                    "op_id": int(r["ID"]),
                    "tt_id": int(r["TT_ID"]),
                    "operation_code": r["OPERATION_CODE"],
                    "ord": int(r["ORD"]),
                    "duration_min": float(r["DURATION_MIN"] or 0),
                    "plan_start": r["PLAN_START"],
                    "plan_end": r["PLAN_END"],
                    "fact_start": r["FACT_START"],
                    "fact_end": r["FACT_END"],
                    "delta_min": delta,
                    "note": r["NOTE"],
                }
            )
        return result

    def update_operation_fact(self, op_id: int, data: OperationFactUpdate) -> dict:
        """Обновляет fact_start / fact_end операции."""
        sets = []
        params: dict[str, Any] = {"op_id": op_id}

        if data.fact_start is not None:
            sets.append("FACT_START = TO_DATE(:fact_start, 'YYYY-MM-DD HH24:MI')")
            params["fact_start"] = data.fact_start
        if data.fact_end is not None:
            sets.append("FACT_END = TO_DATE(:fact_end, 'YYYY-MM-DD HH24:MI')")
            params["fact_end"] = data.fact_end
        if data.note is not None:
            sets.append("NOTE = :note")
            params["note"] = data.note

        if not sets:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")

        rows_updated = self.gateway.execute(
            f"UPDATE RABAEV.RRL_TT_OPERATIONS SET {', '.join(sets)} WHERE ID = :op_id",
            params,
        )
        if not rows_updated:
            raise HTTPException(status_code=404, detail=f"Operation {op_id} not found")

        return {"op_id": op_id, "updated": True}

    def get_vehicles_gantt(self, gantt_date: date) -> list[dict]:
        """Данные Ганта для всех машин на день."""
        # Найти рейсы на дату
        tasks = self.gateway.fetch_all(
            """
            SELECT TT.ID AS TT_ID, TT.TRANSPORT AS VEHICLE_NUM, TT.TRANSTYPE AS VEHICLE_TYPE,
                   V.ID AS VEHICLE_ID
              FROM RABAEV.RRL_TRANSPORT_TASK TT
              LEFT JOIN RABAEV.RRL_TRANSPORTS V ON V.GNUM = TT.TRANSPORT
             WHERE TT.SHIPMENT_DATE = TO_DATE(:d, 'YYYY-MM-DD')
               AND TT.STATUS NOT IN ('Deleted', 'Удалён')
            """,
            {"d": str(gantt_date)},
        )

        result = []
        seen_vehicles: set[str] = set()
        for t in tasks:
            vnum = t.get("VEHICLE_NUM") or ""
            if vnum in seen_vehicles:
                # Merge operations into existing vehicle entry
                for entry in result:
                    if entry["vehicle_num"] == vnum:
                        entry["operations"].extend(
                            self.get_operations(int(t["TT_ID"]))
                        )
                continue
            seen_vehicles.add(vnum)
            result.append(
                {
                    "vehicle_id": int(t["VEHICLE_ID"] or 0),
                    "vehicle_num": vnum,
                    "vehicle_type": t.get("VEHICLE_TYPE") or "",
                    "operations": self.get_operations(int(t["TT_ID"])),
                }
            )

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

        # All active vehicles
        vehicles = self.list_vehicles(active_only=True)

        # Last PLAN_END per vehicle for that day (from RRL_TT_OPERATIONS via task join)
        rows = self.gateway.fetch_all(
            """
            SELECT V.NUM AS VEHICLE_NUM, V.ID AS VEHICLE_ID, V.MARKA, V.TR_TYPE,
                   V.PALLETS AS MAX_PALLETS, V.GIDROBORT,
                   MAX(TO_CHAR(OPS.PLAN_END, 'YYYY-MM-DD HH24:MI')) AS LAST_OP_END
              FROM RABAEV.RRL_TR_VEHICLE V
              LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT
                ON TT.TRANSPORT = V.NUM
               AND TT.SHIPMENT_DATE = TO_DATE(:d, 'YYYY-MM-DD')
               AND TT.STATUS NOT IN ('Deleted', 'Удалён')
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
        """Привязывает рейсы к биллинг-заказу через Oracle-процедуру."""
        for tt_id in tt_ids:
            self.gateway.execute(
                "BEGIN RABAEV.RRL_ADD_TT_2_BILLINGORDER(:tt_id, :order_id); END;",
                {"tt_id": tt_id, "order_id": order_id},
            )

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
        self.gateway.execute(
            "BEGIN RABAEV.RRL_CLOSE_BILLINGORDER(:order_id); END;",
            {"order_id": order_id},
        )
        return self.get_billing_order(order_id) or {"order_id": order_id, "closed": 1}

    def pay_billing_order(self, order_id: int) -> dict:
        """Отмечает биллинг-заказ как оплаченный через Oracle-процедуру."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        if order["payed"]:
            raise HTTPException(status_code=409, detail="Заказ уже оплачен")
        self.gateway.execute(
            "BEGIN RABAEV.RRL_PAY_BILLINGORDER(:order_id); END;",
            {"order_id": order_id},
        )
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
        ship_date = str(task.get("SHIPMENT_DATE") or "")[:10]
        if not ship_date:
            from datetime import date as _date
            ship_date = str(_date.today())

        order_id = self.create_billing_order(company=company, date_from=ship_date, date_to=ship_date)
        self.add_tasks_to_order(order_id, [tt_id])

        return self.get_task_billing(tt_id) or {"order_id": order_id}

    def get_billing_order_tasks(self, order_id: int) -> list[dict]:
        """Список рейсов в биллинг-заказе."""
        rows = self.gateway.fetch_all(
            """
            SELECT TT.ID, TT.TRANSPORT, TT.STATUS, TT.PRICE,
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
                "status": r.get("STATUS"),
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
        # RRL_UPDATE_PRICE обновляет PRICE в БД и возвращает новое значение
        rows = self.gateway.fetch_all(
            "SELECT RABAEV.RRL_UPDATE_PRICE(:tt_id) AS PRICE FROM DUAL",
            {"tt_id": task_id},
        )
        new_price = float(rows[0]["PRICE"] or 0) if rows else 0.0
        return {"task_id": task_id, "price": new_price}

    def list_billing_companies(self) -> list[str]:
        """Справочник транспортных компаний из RRL_BILL_COMPANY."""
        rows = self.gateway.fetch_all(
            """
            SELECT COMPANYNAME
              FROM RABAEV.RRL_BILL_COMPANY
             WHERE DELETED = 0
             ORDER BY POS
            """,
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
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")

        tasks = self.get_billing_order_tasks(order_id)

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

    def export_billing_registry_xlsx(
        self,
        company: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        closed: int | None = None,
        payed: int | None = None,
    ) -> bytes:
        """Генерирует XLSX-реестр всех счетов по фильтру (Sprint 27)."""
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        orders = self.list_billing_orders(company, date_from, date_to, closed, payed)

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

    def remove_task_from_billing_order(self, order_id: int, tt_id: int) -> dict:
        """Отвязывает рейс от биллинг-заказа (обнуляет PAY_ORDER_ID)."""
        order = self.get_billing_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Billing order {order_id} not found")
        if order.get("closed"):
            raise HTTPException(status_code=409, detail="Нельзя изменить закрытый счёт")
        rowcount = self.gateway.execute(
            "BEGIN UPDATE RABAEV.RRL_TRANSPORT_TASK SET PAY_ORDER_ID = NULL "
            "WHERE ID = :tt_id AND PAY_ORDER_ID = :order_id; END;",
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
        date_to: date | None = None,
        no_payments_only: bool = False,
    ) -> bytes:
        """Генерирует XLSX-список рейсов (Sprint 28, ТЗ §3 «В Excel»)."""
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        tasks = self.list_tasks(
            shipment_date=shipment_date,
            condition=condition,
            task_id=task_id,
            transport_mask=transport_mask,
            company_mask=company_mask,
            date_to=date_to,
            no_payments_only=no_payments_only,
        )

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
                   TT.STATUS
              FROM RABAEV.RRL_TRANSPORT_TASK TT
             WHERE TT.SHIPMENT_DATE BETWEEN TO_DATE(:d_from, 'YYYY-MM-DD')
                                        AND TO_DATE(:d_to,   'YYYY-MM-DD')
               AND TT.STATUS NOT IN ('Deleted', 'Удалён')
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
