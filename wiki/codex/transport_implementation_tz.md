# ТЗ: Реализация модуля планирования рейсов и управления транспортом
### Максимально детальная версия · AI-ассистент · 2026-05-21

> Этот файл — исчерпывающее руководство к реализации.
> Источники: transport_final_tz.md, transport_dispatch_assignment_tz.md,
> transport_management_tz.md, анализ Form1.cs + Oracle DDL.

---

## Содержание

1. [Принципы и контекст](#1-принципы-и-контекст)
2. [Фаза 0: Oracle — миграции и пакет](#2-фаза-0-oracle)
3. [Фаза 1: FastAPI — базовые эндпоинты](#3-фаза-1-fastapi)
4. [Фаза 2: React — ручной режим](#4-фаза-2-react-ручной-режим)
5. [Фаза 3: React — полу-авто, карта, метрики](#5-фаза-3-react-полу-авто)
6. [Фаза 4: OSRM и матрица расстояний](#6-фаза-4-osrm)
7. [Фаза 5: OR-Tools и шаблонный движок](#7-фаза-5-vrp-solvers)
8. [Фаза 6: Attention Model и воркеры](#8-фаза-6-attention-model)
9. [Фаза 7: React — панель авто-плана](#9-фаза-7-react-авто-план)
10. [Фаза 8: Load-тесты и evidence](#10-фаза-8-тесты)

---

## 1. Принципы и контекст

### 1.1 Неизменные правила

| Правило | Обоснование |
|---------|------------|
| Все мутации только через `RRL_TRANSPORT_API` | C# работает параллельно, нельзя сломать |
| C# не трогаем | Диспетчеры мигрируют постепенно |
| Oracle — система отсчёта | FastAPI читает из Oracle, пишет через пакет |
| Всё через `RRL_API_CALL_LOG` | Аудит-трейл для всех операций |
| Координаты уже есть | `RRL_ADDR.SHIROTA / DOLGOTA` — не добавлять, использовать |

### 1.2 Стек реализации

```
Oracle 11g     → PL/SQL-пакет RRL_TRANSPORT_API + миграции 044–045
FastAPI        → api/wms_api_server/app/routers/transport.py
               → api/wms_api_server/app/services/transport_service.py
               → api/wms_api_server/app/services/vrp_service.py
React 19       → admin/wms_admin_frontend/src/components/Transport/
Python         → scipy, scikit-learn, ortools, torch (опционально)
OSRM           → Docker self-hosted :5000
```

### 1.3 Единица назначения

**СТ (сборочное задание)** — атомарная единица. Одно СТ = все паллеты одного адреса одного заказа.
`RRL_TT_ADD_PALL(TT_ID, ST_NUMBER, user_id)` назначает СТ целиком — не паллеты по одной.

---

## 2. Фаза 0: Oracle

### 2.1 Миграция 044 — расширение таблиц

```sql
-- Файл: db/migrations/044_transport_capacity_windows.sql

-- Вместимость ТС по весу и объёму
ALTER TABLE RABAEV.RRL_TR_VEHICLE ADD (
  WEIGHT_CAPACITY  NUMBER(8,0)  DEFAULT NULL,  -- кг, NULL = не задана
  VOLUME_CAPACITY  NUMBER(6,2)  DEFAULT NULL   -- м³, NULL = не задана
);
COMMENT ON COLUMN RABAEV.RRL_TR_VEHICLE.WEIGHT_CAPACITY IS 'Грузоподъёмность, кг';
COMMENT ON COLUMN RABAEV.RRL_TR_VEHICLE.VOLUME_CAPACITY IS 'Объём кузова, м³';

-- Временны́е окна и время обслуживания адресов
ALTER TABLE RABAEV.RRL_ADDR ADD (
  SERVICE_MIN          NUMBER(3,0)  DEFAULT 15,   -- минут на остановку
  DELIVERY_TIME_FROM   VARCHAR2(5)  DEFAULT NULL,  -- HH:MM
  DELIVERY_TIME_TO     VARCHAR2(5)  DEFAULT NULL   -- HH:MM
);
COMMENT ON COLUMN RABAEV.RRL_ADDR.SERVICE_MIN IS 'Время обслуживания на адресе, мин';
COMMENT ON COLUMN RABAEV.RRL_ADDR.DELIVERY_TIME_FROM IS 'Начало временного окна HH:MM';
COMMENT ON COLUMN RABAEV.RRL_ADDR.DELIVERY_TIME_TO IS 'Конец временного окна HH:MM';

-- Вью доступных СТ
CREATE OR REPLACE VIEW RABAEV.RRL_V_AVAILABLE_STS AS
SELECT
  P.ST_NUMBER,
  P.ADDR,
  A.REGION,
  A.RAION,
  A.ORD,
  A.SHIROTA,
  A.DOLGOTA,
  A.SERVICE_MIN,
  A.DELIVERY_TIME_FROM,
  A.DELIVERY_TIME_TO,
  NVL(A.TRANSPORT_TYPE, '0')                          AS TRANSPORT_TYPE,
  NVL(A.STOL, 0)                                      AS NEEDS_HYDRO_BOARD,
  P.WARE_ID,
  COUNT(DISTINCT P.PALLET_UID)                         AS PALLETS_COUNT,
  ROUND(SUM(NVL(R.ORDER_WEIGHT,0)), 0)                 AS WEIGHT_KG,
  ROUND(SUM(NVL(R.TARESIZE,0) * NVL(R.PACK_COUNT,0))
        / 1000000, 2)                                  AS VOLUME_M3,
  RABAEV.RRL_ST_VERYFY_PERC(P.ST_NUMBER)              AS VERIFY_PCT,
  MIN(P.STDATE)                                        AS STDATE,
  MAX(P.TRANSTASK_ID)                                  AS TRANSTASK_ID
FROM RABAEV.RRL_SBORKA_PALLETS P
JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R ON R.PALLET_UID = P.PALLET_UID
LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
WHERE (P.DELETED IS NULL OR P.DELETED <> 1)
GROUP BY
  P.ST_NUMBER, P.ADDR, A.REGION, A.RAION, A.ORD,
  A.SHIROTA, A.DOLGOTA, A.SERVICE_MIN,
  A.DELIVERY_TIME_FROM, A.DELIVERY_TIME_TO,
  P.WARE_ID, A.TRANSPORT_TYPE, A.STOL;

-- Индексы для API-запросов
CREATE INDEX IDX_SP_TRANSTASK ON RABAEV.RRL_SBORKA_PALLETS (TRANSTASK_ID, DELETED);
CREATE INDEX IDX_SP_STDATE    ON RABAEV.RRL_SBORKA_PALLETS (STDATE, DELETED);
CREATE INDEX IDX_TT_SHIPDATE  ON RABAEV.RRL_TRANSPORT_TASK (SHIPMENT_DATE, DELETED);
```

### 2.2 Миграция 045 — новые таблицы для VRP и шаблонов

```sql
-- Файл: db/migrations/045_transport_vrp_tables.sql

-- Кэш дорожной матрицы (OSRM)
CREATE TABLE RABAEV.RRL_ADDR_DISTANCE_MATRIX (
  ADDR_FROM       VARCHAR2(200) NOT NULL,
  ADDR_TO         VARCHAR2(200) NOT NULL,
  DIST_METERS     NUMBER(10,0),
  DURATION_SEC    NUMBER(10,0),
  CALC_DATE       DATE DEFAULT SYSDATE NOT NULL,
  CONSTRAINT PK_DIST_MATRIX PRIMARY KEY (ADDR_FROM, ADDR_TO)
);
CREATE INDEX IDX_DIST_FROM     ON RABAEV.RRL_ADDR_DISTANCE_MATRIX (ADDR_FROM);
CREATE INDEX IDX_DIST_CALCDATE ON RABAEV.RRL_ADDR_DISTANCE_MATRIX (CALC_DATE);

-- Шаблоны маршрутов (накапливаются автоматически)
CREATE TABLE RABAEV.RRL_TT_ROUTE_TEMPLATE (
  ID              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  DOW             NUMBER(1)     NOT NULL,  -- 1=пн … 7=вс
  TRANSTYPE       VARCHAR2(20)  NOT NULL,
  ADDR_SIGNATURE  VARCHAR2(4000) NOT NULL, -- sorted(addrs).join(',') — ключ поиска
  ADDR_LIST       CLOB,                    -- JSON [{addr,ord,avg_pallets,lat,lon}]
  TOTAL_KM        NUMBER(8,2),
  TOTAL_HOURS     NUMBER(5,2),
  USAGE_COUNT     NUMBER DEFAULT 0,
  LAST_USED       DATE,
  QUALITY_SCORE   NUMBER(5,3) DEFAULT 0.5,
  CREATED_BY      VARCHAR2(100) DEFAULT 'AUTO',
  CREATE_DATE     DATE DEFAULT SYSDATE
);
CREATE INDEX IDX_TMPL_DOW ON RABAEV.RRL_TT_ROUTE_TEMPLATE (DOW, TRANSTYPE);

-- Правки диспетчера для RL-обучения
CREATE TABLE RABAEV.RRL_TT_RL_CORRECTIONS (
  ID            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  DATE_OF_PLAN  DATE         NOT NULL,
  ST_NUMBER     VARCHAR2(50) NOT NULL,
  FROM_TASK_IDX NUMBER,
  TO_TASK_IDX   NUMBER,
  ADDR_FROM     VARCHAR2(200),
  ADDR_TO       VARCHAR2(200),
  DOW           NUMBER(1),
  TRANSTYPE     VARCHAR2(20),
  CREATE_DATE   DATE DEFAULT SYSDATE
);
CREATE INDEX IDX_RL_DOW_TYPE ON RABAEV.RRL_TT_RL_CORRECTIONS (DOW, TRANSTYPE);

-- Аудит сессий авто-планирования
CREATE TABLE RABAEV.RRL_TT_AUTO_PLAN_SESSION (
  ID                NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  PLAN_DATE         DATE          NOT NULL,
  SOLVER_USED       VARCHAR2(50),   -- 'template'/'ortools'/'attention'
  INPUT_ST_COUNT    NUMBER,
  RESULT_TASK_COUNT NUMBER,
  TOTAL_KM          NUMBER(8,2),
  ACCEPTED_BY       VARCHAR2(100),
  ACCEPTED_AT       DATE,
  EDITS_COUNT       NUMBER DEFAULT 0,
  SESSION_JSON      CLOB            -- полный snapshot для отладки
);
```

### 2.3 Пакет RRL_TRANSPORT_API — спецификация

```sql
-- Файл: db/packages/rrl_transport_api.pks

CREATE OR REPLACE PACKAGE RABAEV.RRL_TRANSPORT_API AS

  -- Жизненный цикл рейса
  PROCEDURE create_task(
    p_transtype       IN  VARCHAR2,
    p_shipment_date   IN  DATE,
    p_user_id         IN  VARCHAR2,
    p_task_id         OUT NUMBER
  );

  PROCEDURE update_task(
    p_task_id              IN NUMBER,
    p_vehicle_num          IN VARCHAR2  DEFAULT NULL,
    p_driver_id            IN NUMBER    DEFAULT NULL,
    p_dock                 IN VARCHAR2  DEFAULT NULL,
    p_shipment_date        IN DATE      DEFAULT NULL,
    p_planned_delivery     IN DATE      DEFAULT NULL,
    p_primechanie          IN VARCHAR2  DEFAULT NULL,
    p_user_id              IN VARCHAR2
  );

  PROCEDURE close_task(
    p_task_id   IN NUMBER,
    p_user_id   IN VARCHAR2
  );

  PROCEDURE cancel_task(
    p_task_id   IN NUMBER,
    p_user_id   IN VARCHAR2
  );

  -- Управление составом рейса
  PROCEDURE assign_st_list(
    p_task_id   IN  NUMBER,
    p_st_list   IN  SYS.ODCIVARCHAR2LIST,  -- ['0441','0442',...]
    p_user_id   IN  VARCHAR2,
    p_warnings  OUT VARCHAR2               -- JSON массив предупреждений
  );

  PROCEDURE unassign_st(
    p_task_id   IN NUMBER,
    p_st_number IN VARCHAR2,
    p_user_id   IN VARCHAR2
  );

  -- p_st_ords: SYS.ODCIVARCHAR2LIST формата ['ST_NUMBER:NEW_ORD', ...]
  PROCEDURE reorder_by_sequence(
    p_task_id  IN NUMBER,
    p_st_ords  IN SYS.ODCIVARCHAR2LIST
  );

  -- Данные
  FUNCTION get_available_sts(
    p_date           IN DATE,
    p_unassigned_only IN NUMBER DEFAULT 1,  -- 1=только свободные
    p_addr_mask      IN VARCHAR2 DEFAULT NULL,
    p_region         IN VARCHAR2 DEFAULT NULL,
    p_transtype      IN VARCHAR2 DEFAULT NULL,
    p_ware_id        IN NUMBER   DEFAULT NULL
  ) RETURN SYS_REFCURSOR;

END RRL_TRANSPORT_API;
/
```

### 2.4 Пакет RRL_TRANSPORT_API — тело (ключевые процедуры)

```sql
-- Файл: db/packages/rrl_transport_api.pkb

CREATE OR REPLACE PACKAGE BODY RABAEV.RRL_TRANSPORT_API AS

  PROCEDURE create_task(
    p_transtype     IN  VARCHAR2,
    p_shipment_date IN  DATE,
    p_user_id       IN  VARCHAR2,
    p_task_id       OUT NUMBER
  ) IS
  BEGIN
    p_task_id := RABAEV.RRL_TRASPORT_TASK_ADD(
      p_transtype,
      p_shipment_date,
      p_user_id
    );
    -- Лог
    INSERT INTO RABAEV.RRL_API_CALL_LOG
      (METHOD, ENTITY_TYPE, ENTITY_ID, USER_ID, REQUEST_TS)
    VALUES
      ('transport.create_task', 'TRANSPORT_TASK', p_task_id, p_user_id, SYSDATE);
    COMMIT;
  END;

  PROCEDURE assign_st_list(
    p_task_id   IN  NUMBER,
    p_st_list   IN  SYS.ODCIVARCHAR2LIST,
    p_user_id   IN  VARCHAR2,
    p_warnings  OUT VARCHAR2
  ) IS
    v_warnings VARCHAR2(4000) := '[]';
    v_warn_arr VARCHAR2(4000) := '';
    v_st       VARCHAR2(50);
    v_existing NUMBER;
  BEGIN
    FOR i IN 1 .. p_st_list.COUNT LOOP
      v_st := p_st_list(i);

      -- Проверяем: не назначен ли уже на другой рейс
      SELECT COUNT(*) INTO v_existing
        FROM RABAEV.RRL_SBORKA_PALLETS
       WHERE ST_NUMBER = v_st
         AND TRANSTASK_ID IS NOT NULL
         AND TRANSTASK_ID <> p_task_id
         AND (DELETED IS NULL OR DELETED <> 1)
         AND ROWNUM = 1;

      IF v_existing > 0 THEN
        v_warn_arr := v_warn_arr ||
          '{"st":"' || v_st || '","msg":"already_assigned"},';
      END IF;

      -- Назначаем (оригинальная функция C#)
      RABAEV.RRL_TT_ADD_PALL(p_task_id, v_st, p_user_id);
    END LOOP;

    -- Пересортировать по ORD адресов
    RABAEV.RRL_TT_REORDER_ADR(p_task_id);

    IF v_warn_arr IS NOT NULL THEN
      p_warnings := '[' || RTRIM(v_warn_arr, ',') || ']';
    END IF;

    COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE;
  END;

  PROCEDURE unassign_st(
    p_task_id   IN NUMBER,
    p_st_number IN VARCHAR2,
    p_user_id   IN VARCHAR2
  ) IS
  BEGIN
    -- RRL_TT_ADD_PALL с NULL task_id снимает назначение
    UPDATE RABAEV.RRL_SBORKA_PALLETS
       SET TRANSTASK_ID = NULL
     WHERE ST_NUMBER = p_st_number
       AND TRANSTASK_ID = p_task_id;

    RABAEV.RRL_TT_REORDER_ADR(p_task_id);
    COMMIT;
  END;

  PROCEDURE reorder_by_sequence(
    p_task_id  IN NUMBER,
    p_st_ords  IN SYS.ODCIVARCHAR2LIST
  ) IS
    v_parts  SYS.ODCIVARCHAR2LIST;
    v_st     VARCHAR2(50);
    v_ord    NUMBER;
    v_sep    NUMBER;
  BEGIN
    FOR i IN 1 .. p_st_ords.COUNT LOOP
      v_sep := INSTR(p_st_ords(i), ':');
      v_st  := SUBSTR(p_st_ords(i), 1, v_sep - 1);
      v_ord := TO_NUMBER(SUBSTR(p_st_ords(i), v_sep + 1));

      UPDATE RABAEV.RRL_SBORKA_PALLETS
         SET ORD = v_ord
       WHERE ST_NUMBER = v_st
         AND TRANSTASK_ID = p_task_id;
    END LOOP;
    COMMIT;
  END;

  FUNCTION get_available_sts(
    p_date            IN DATE,
    p_unassigned_only IN NUMBER DEFAULT 1,
    p_addr_mask       IN VARCHAR2 DEFAULT NULL,
    p_region          IN VARCHAR2 DEFAULT NULL,
    p_transtype       IN VARCHAR2 DEFAULT NULL,
    p_ware_id         IN NUMBER   DEFAULT NULL
  ) RETURN SYS_REFCURSOR IS
    v_cur SYS_REFCURSOR;
  BEGIN
    OPEN v_cur FOR
      SELECT * FROM RABAEV.RRL_V_AVAILABLE_STS V
       WHERE TRUNC(V.STDATE) = TRUNC(p_date)
         AND (p_unassigned_only = 0 OR V.TRANSTASK_ID IS NULL)
         AND (p_addr_mask IS NULL OR
              UPPER(V.ADDR) LIKE '%' || UPPER(p_addr_mask) || '%')
         AND (p_region    IS NULL OR V.REGION    = p_region)
         AND (p_transtype IS NULL OR V.TRANSPORT_TYPE = p_transtype)
         AND (p_ware_id   IS NULL OR V.WARE_ID   = p_ware_id)
       ORDER BY V.RAION, V.ORD;
    RETURN v_cur;
  END;

END RRL_TRANSPORT_API;
/
```

---

## 3. Фаза 1: FastAPI

### 3.1 Структура файлов

```
api/wms_api_server/app/
  routers/
    transport.py          ← все HTTP-эндпоинты
  services/
    transport_service.py  ← бизнес-логика, вызовы Oracle
    vrp_service.py        ← VRP-алгоритмы (фаза 4–6)
  models/
    transport.py          ← Pydantic-схемы
  workers/
    vrp_matrix_worker.py
    attention_train_worker.py
    template_cleanup_worker.py
```

### 3.2 Pydantic-модели

```python
# api/wms_api_server/app/models/transport.py

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class VehicleInfo(BaseModel):
    id: int
    num: str
    marka: Optional[str]
    pallets: Optional[int]
    weight_capacity: Optional[float]
    volume_capacity: Optional[float]
    gidrobort: bool

class DriverInfo(BaseModel):
    id: int
    full_name: str
    tel: Optional[str]

class AvailableST(BaseModel):
    st_number: str
    addr: str
    region: Optional[str]
    raion: Optional[str]
    ord: int
    lat: Optional[float]          # SHIROTA
    lon: Optional[float]          # DOLGOTA
    service_min: int = 15
    delivery_time_from: Optional[str]
    delivery_time_to: Optional[str]
    ware_id: int
    transport_type: Optional[str]
    needs_hydro_board: bool = False
    pallets_count: int
    weight_kg: float
    volume_m3: float
    verify_pct: int
    stdate: datetime
    transtask_id: Optional[int]

class TransportTaskCard(BaseModel):
    id: int
    condition: str
    transtype: str
    shipment_date: date
    shipment_time: Optional[datetime]
    vehicle: Optional[VehicleInfo]
    driver: Optional[DriverInfo]
    dock: Optional[str]
    dock_from: Optional[datetime]
    dock_to: Optional[datetime]
    pallets_count: int
    pallets_capacity: Optional[int]
    weight_kg: float
    weight_capacity: Optional[float]
    volume_m3: float
    volume_capacity: Optional[float]
    distance_km: Optional[float]    # Haversine-цепочка
    estimated_hours: Optional[float]
    estimated_cost: Optional[float]
    regions: Optional[str]
    price: Optional[float]
    primechanie: Optional[str]
    warnings: list[str] = []

class TaskPalletRow(BaseModel):
    st_number: str
    addr: str
    pallets_count: int
    weight_kg: float
    ord: int
    verify_pct: int
    lat: Optional[float]
    lon: Optional[float]
    delivery_time_from: Optional[str]
    delivery_time_to: Optional[str]
    needs_hydro_board: bool

class TaskCreate(BaseModel):
    transtype: str
    shipment_date: date
    st_numbers: list[str] = []

class TaskUpdate(BaseModel):
    vehicle_num: Optional[str] = None
    driver_id: Optional[int] = None
    dock: Optional[str] = None
    shipment_date: Optional[date] = None
    planned_delivery_date: Optional[date] = None
    primechanie: Optional[str] = None

class AssignRequest(BaseModel):
    st_numbers: list[str] = Field(..., min_items=1)

class ReorderRequest(BaseModel):
    # [{st_number: "0441", new_ord: 1}, ...]
    sequence: list[dict]

class DaySummary(BaseModel):
    total_sts: int
    total_pallets: int
    assigned_pallets: int
    unassigned_pallets: int
    available_vehicles: int
    total_vehicle_capacity: int
    coverage_ok: bool

class DockSlot(BaseModel):
    dock: str
    task_id: int
    task_condition: str
    time_from: Optional[datetime]
    time_to: Optional[datetime]
    pallets_count: int
```

### 3.3 Transport Service

```python
# api/wms_api_server/app/services/transport_service.py

import math
from datetime import date
from typing import Optional
from ..db import get_oracle_conn
from ..models.transport import (
    TransportTaskCard, AvailableST, TaskPalletRow,
    DaySummary, DockSlot
)

AVG_SPEED_KMH = 40.0


def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Расстояние между двумя точками в км."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def _calc_route_km(pallets: list[TaskPalletRow],
                   depot_lat: float, depot_lon: float) -> Optional[float]:
    """Суммарный Haversine-путь: склад → адр1 → … → склад."""
    points = [(depot_lat, depot_lon)]
    for p in sorted(pallets, key=lambda x: x.ord):
        if p.lat and p.lon:
            points.append((p.lat, p.lon))
    if len(points) < 2:
        return None
    points.append((depot_lat, depot_lon))
    return sum(
        _haversine(points[i][0], points[i][1],
                   points[i+1][0], points[i+1][1])
        for i in range(len(points) - 1)
    )


def get_tasks(shipment_date: date, conn) -> list[TransportTaskCard]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.ID, T.CONDITION, T.TRANSTYPE, T.SHIPMENT_DATE, T.SHIPMENT_TIME,
               V.ID VEH_ID, V.NUM VEH_NUM, V.MARKA, V.PALLETS,
               V.WEIGHT_CAPACITY, V.VOLUME_CAPACITY, NVL(V.GIDROBORT,0),
               D.ID DRV_ID, D.F||' '||SUBSTR(D.I,1,1)||'.'||SUBSTR(D.O,1,1)||'.' DRVNAME,
               D.TEL, T.DOCK, T.DOCK_REZERV_TIME_FROM, T.DOCK_REZERV_TIME_TO,
               T.PRICE, T.TEMP_REGION, T.PRIMECHANIE,
               RABAEV.RRL_TT_PALLETS(T.ID)   PALL_CNT,
               RABAEV.RRL_TT_WEIGHT(T.ID)    WEIGHT,
               RABAEV.RRL_TT_VOLUME(T.ID)    VOLUME
          FROM RABAEV.RRL_TRANSPORT_TASK T
          LEFT JOIN RABAEV.RRL_TR_VEHICLE V ON V.NUM = T.TRANSPORT
          LEFT JOIN RABAEV.RRL_TR_VODITEL D ON D.ID  = T.VODITEL_ID
         WHERE TRUNC(T.SHIPMENT_DATE) = TRUNC(:1)
           AND (T.DELETED IS NULL OR T.DELETED <> 1)
         ORDER BY T.SHIPMENT_DATE
    """, [shipment_date])
    rows = cursor.fetchall()
    result = []
    for r in rows:
        result.append(TransportTaskCard(
            id=r[0], condition=r[1] or 'CREATED',
            transtype=r[2], shipment_date=r[3],
            shipment_time=r[4],
            vehicle={"id":r[5],"num":r[6],"marka":r[7],
                     "pallets":r[8],"weight_capacity":r[9],
                     "volume_capacity":r[10],"gidrobort":bool(r[11])}
                     if r[5] else None,
            driver={"id":r[12],"full_name":r[13],"tel":r[14]}
                   if r[12] else None,
            dock=r[15], dock_from=r[16], dock_to=r[17],
            price=r[18], regions=r[19], primechanie=r[20],
            pallets_count=int(r[21] or 0),
            weight_kg=float(r[22] or 0),
            volume_m3=float(r[23] or 0),
            pallets_capacity=r[8],
            weight_capacity=r[9], volume_capacity=r[10],
        ))
    return result


def get_available_sts(
    shipment_date: date,
    unassigned_only: bool,
    addr_mask: Optional[str],
    region: Optional[str],
    conn
) -> list[AvailableST]:
    ref_cursor = conn.cursor()
    ref_cursor.callproc("RABAEV.RRL_TRANSPORT_API.GET_AVAILABLE_STS", [
        shipment_date,
        1 if unassigned_only else 0,
        addr_mask, region, None, None,
        ref_cursor
    ])
    rows = ref_cursor.fetchall()
    cols = [d[0].lower() for d in ref_cursor.description]
    return [AvailableST(**dict(zip(cols, r))) for r in rows]


def create_task(transtype: str, shipment_date: date,
                st_numbers: list[str], user_id: str, conn) -> int:
    task_id_var = conn.cursor()
    task_id_var.callproc("RABAEV.RRL_TRANSPORT_API.CREATE_TASK", [
        transtype, shipment_date, user_id, task_id_var
    ])
    task_id = task_id_var.getvalue()

    if st_numbers:
        warnings_var = conn.cursor()
        conn.cursor().callproc("RABAEV.RRL_TRANSPORT_API.ASSIGN_ST_LIST", [
            task_id,
            conn.cursor().arrayvar(str, st_numbers),
            user_id,
            warnings_var
        ])
    return task_id


def assign_sts(task_id: int, st_numbers: list[str],
               user_id: str, conn) -> list[str]:
    warnings_out = conn.cursor()
    cur = conn.cursor()
    cur.callproc("RABAEV.RRL_TRANSPORT_API.ASSIGN_ST_LIST", [
        task_id,
        cur.arrayvar(str, st_numbers),
        user_id,
        warnings_out
    ])
    import json
    w = warnings_out.getvalue()
    return json.loads(w) if w else []


def unassign_st(task_id: int, st_number: str, user_id: str, conn):
    conn.cursor().callproc("RABAEV.RRL_TRANSPORT_API.UNASSIGN_ST", [
        task_id, st_number, user_id
    ])


def get_day_summary(shipment_date: date, conn) -> DaySummary:
    cur = conn.cursor()
    cur.execute("""
        SELECT
          COUNT(DISTINCT ST_NUMBER)               total_sts,
          SUM(PALLETS_COUNT)                      total_pallets,
          SUM(CASE WHEN TRANSTASK_ID IS NOT NULL
                   THEN PALLETS_COUNT ELSE 0 END) assigned_pallets,
          SUM(CASE WHEN TRANSTASK_ID IS NULL
                   THEN PALLETS_COUNT ELSE 0 END) unassigned_pallets
        FROM RABAEV.RRL_V_AVAILABLE_STS
        WHERE TRUNC(STDATE) = TRUNC(:1)
    """, [shipment_date])
    r = cur.fetchone()
    total_sts, total_p, assigned_p, unassigned_p = r

    cur.execute("""
        SELECT COUNT(*), NVL(SUM(PALLETS), 0)
          FROM RABAEV.RRL_TR_VEHICLE
         WHERE WORKING_NOW = 1 AND (BLOCKED IS NULL OR BLOCKED = 0)
           AND (DELETED IS NULL OR DELETED <> 1)
    """)
    r2 = cur.fetchone()
    avail_v, capacity = r2

    return DaySummary(
        total_sts=total_sts or 0,
        total_pallets=total_p or 0,
        assigned_pallets=assigned_p or 0,
        unassigned_pallets=unassigned_p or 0,
        available_vehicles=avail_v or 0,
        total_vehicle_capacity=capacity or 0,
        coverage_ok=(capacity or 0) >= (unassigned_p or 0),
    )
```

### 3.4 Router

```python
# api/wms_api_server/app/routers/transport.py

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date
from typing import Optional
from ..db import get_oracle_conn
from ..services import transport_service as svc
from ..models.transport import (
    TaskCreate, TaskUpdate, AssignRequest, ReorderRequest,
    TransportTaskCard, AvailableST, DaySummary
)

router = APIRouter(prefix="/transport", tags=["transport"])


@router.get("/tasks", response_model=list[TransportTaskCard])
def get_tasks(
    date: date = Query(...),
    conn=Depends(get_oracle_conn)
):
    return svc.get_tasks(date, conn)


@router.post("/tasks", response_model=dict)
def create_task(
    body: TaskCreate,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    task_id = svc.create_task(
        body.transtype, body.shipment_date,
        body.st_numbers, user_id, conn
    )
    return {"task_id": task_id}


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    body: TaskUpdate,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    conn.cursor().callproc("RABAEV.RRL_TRANSPORT_API.UPDATE_TASK", [
        task_id, body.vehicle_num, body.driver_id, body.dock,
        body.shipment_date, body.planned_delivery_date,
        body.primechanie, user_id
    ])
    return {"ok": True}


@router.post("/tasks/{task_id}/assign")
def assign_sts(
    task_id: int,
    body: AssignRequest,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    warnings = svc.assign_sts(task_id, body.st_numbers, user_id, conn)
    return {"ok": True, "warnings": warnings}


@router.delete("/tasks/{task_id}/st/{st_number}")
def unassign_st(
    task_id: int,
    st_number: str,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    svc.unassign_st(task_id, st_number, user_id, conn)
    return {"ok": True}


@router.post("/tasks/{task_id}/close")
def close_task(
    task_id: int,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    conn.cursor().callproc(
        "RABAEV.RRL_TRANSPORT_API.CLOSE_TASK", [task_id, user_id]
    )
    return {"ok": True}


@router.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: int,
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    conn.cursor().callproc(
        "RABAEV.RRL_TRANSPORT_API.CANCEL_TASK", [task_id, user_id]
    )
    return {"ok": True}


@router.get("/pallets/available", response_model=list[AvailableST])
def get_available(
    date: date = Query(...),
    unassigned_only: bool = Query(True),
    addr_mask: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    conn=Depends(get_oracle_conn)
):
    return svc.get_available_sts(date, unassigned_only, addr_mask, region, conn)


@router.get("/planning/summary", response_model=DaySummary)
def get_summary(
    date: date = Query(...),
    conn=Depends(get_oracle_conn)
):
    return svc.get_day_summary(date, conn)


@router.get("/docks/schedule")
def get_dock_schedule(
    date: date = Query(...),
    conn=Depends(get_oracle_conn)
):
    cur = conn.cursor()
    cur.execute("""
        SELECT T.DOCK, T.ID, T.CONDITION,
               T.DOCK_REZERV_TIME_FROM, T.DOCK_REZERV_TIME_TO,
               RABAEV.RRL_TT_PALLETS(T.ID)
          FROM RABAEV.RRL_TRANSPORT_TASK T
         WHERE TRUNC(T.SHIPMENT_DATE) = TRUNC(:1)
           AND T.DOCK IS NOT NULL
           AND (T.DELETED IS NULL OR T.DELETED <> 1)
         ORDER BY T.DOCK, T.DOCK_REZERV_TIME_FROM
    """, [date])
    rows = cur.fetchall()
    return [
        {"dock": r[0], "task_id": r[1], "condition": r[2],
         "time_from": r[3], "time_to": r[4], "pallets_count": r[5]}
        for r in rows
    ]


@router.post("/tasks/{task_id}/optimize-sequence")
def optimize_sequence(
    task_id: int,
    warehouse_lat: float = Query(default=55.75),
    warehouse_lon: float = Query(default=37.61),
    conn=Depends(get_oracle_conn)
):
    from ..services.vrp_service import nearest_neighbour_tsp
    cur = conn.cursor()
    cur.execute("""
        SELECT P.ST_NUMBER, A.SHIROTA, A.DOLGOTA, P.ORD
          FROM RABAEV.RRL_SBORKA_PALLETS P
          LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = P.ADDR
         WHERE P.TRANSTASK_ID = :1
           AND (P.DELETED IS NULL OR P.DELETED <> 1)
         GROUP BY P.ST_NUMBER, A.SHIROTA, A.DOLGOTA, P.ORD
         ORDER BY P.ORD
    """, [task_id])
    rows = cur.fetchall()
    nodes = [
        {"st_number": r[0], "lat": r[1], "lon": r[2], "ord": r[3]}
        for r in rows if r[1] and r[2]
    ]
    optimized = nearest_neighbour_tsp(nodes, warehouse_lat, warehouse_lon)
    return {"proposed_order": optimized}


@router.post("/tasks/{task_id}/optimize-sequence/confirm")
def confirm_sequence(
    task_id: int,
    body: ReorderRequest,
    conn=Depends(get_oracle_conn)
):
    st_ords = [f"{s['st_number']}:{s['new_ord']}" for s in body.sequence]
    cur = conn.cursor()
    arr = cur.arrayvar(str, st_ords)
    cur.callproc("RABAEV.RRL_TRANSPORT_API.REORDER_BY_SEQUENCE",
                 [task_id, arr])
    return {"ok": True}


@router.get("/tasks/{task_id}/manifest")
def get_manifest(task_id: int, conn=Depends(get_oracle_conn)):
    from ..services.transport_service import build_manifest
    return build_manifest(task_id, conn)
```

---

## 4. Фаза 2: React — ручной режим

### 4.1 Структура компонентов

```
src/components/Transport/
  index.tsx                      ← export + lazy imports
  DispatchBoard.tsx              ← root: дата, переключатель режимов
  assignment/
    AssignmentModeView.tsx       ← три панели
    TransportTaskCard.tsx        ← карточка рейса
    AvailableOrdersTable.tsx     ← таблица СТ
    TaskPalletsTable.tsx         ← состав рейса
    NewTaskModal.tsx             ← форма создания рейса
  shared/
    AssignmentSummaryBar.tsx     ← итог P/M/V
    AssignmentWarnings.tsx       ← предупреждения
  hooks/
    useTransportTasks.ts
    useAvailableSTs.ts
    useAssignment.ts
    useRouteMetrics.ts
    useCapacityWarnings.ts
```

### 4.2 DispatchBoard.tsx

```tsx
// src/components/Transport/DispatchBoard.tsx
import React, { useState } from 'react'
import { DatePicker, Segmented } from 'antd'
import dayjs, { Dayjs } from 'dayjs'
import AssignmentModeView from './assignment/AssignmentModeView'
import PlanningModeView from './planning/PlanningModeView'

type Mode = 'assignment' | 'planning'

export default function DispatchBoard() {
  const [date, setDate] = useState<Dayjs>(dayjs())
  const [mode, setMode] = useState<Mode>('assignment')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ padding: '8px 16px', background: '#fff', borderBottom: '1px solid #f0f0f0',
                    display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ fontWeight: 600 }}>Управление рейсами</span>
        <DatePicker value={date} onChange={d => d && setDate(d)} format="DD.MM.YYYY" />
        <Segmented
          value={mode}
          onChange={v => setMode(v as Mode)}
          options={[
            { label: 'Назначение', value: 'assignment' },
            { label: 'Планирование', value: 'planning' },
          ]}
        />
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        {mode === 'assignment'
          ? <AssignmentModeView date={date.toDate()} />
          : <PlanningModeView date={date.toDate()} />
        }
      </div>
    </div>
  )
}
```

### 4.3 useTransportTasks.ts

```typescript
// src/components/Transport/hooks/useTransportTasks.ts
import { useState, useEffect, useCallback } from 'react'
import { apiGet, apiPost, apiDelete, apiPatch } from '../../../api/client'
import type { TransportTask, AvailableST } from '../types'

export function useTransportTasks(date: Date) {
  const [tasks, setTasks]       = useState<TransportTask[]>([])
  const [loading, setLoading]   = useState(false)
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const dateStr = date.toISOString().slice(0, 10)

  const reload = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiGet<TransportTask[]>(`/transport/tasks?date=${dateStr}`)
      setTasks(data)
    } finally {
      setLoading(false)
    }
  }, [dateStr])

  useEffect(() => { reload() }, [reload])

  const assignSTs = async (taskId: number, stNumbers: string[], userId: string) => {
    const res = await apiPost(`/transport/tasks/${taskId}/assign?user_id=${userId}`,
                              { st_numbers: stNumbers })
    await reload()
    return res.warnings as string[]
  }

  const unassignST = async (taskId: number, stNumber: string, userId: string) => {
    await apiDelete(`/transport/tasks/${taskId}/st/${stNumber}?user_id=${userId}`)
    await reload()
  }

  const createTask = async (transtype: string, stNumbers: string[], userId: string) => {
    const res = await apiPost(`/transport/tasks?user_id=${userId}`, {
      transtype,
      shipment_date: dateStr,
      st_numbers: stNumbers,
    })
    await reload()
    setSelectedId(res.task_id)
    return res.task_id as number
  }

  return { tasks, loading, selectedId, setSelectedId, reload, assignSTs, unassignST, createTask }
}
```

### 4.4 useAvailableSTs.ts

```typescript
// src/components/Transport/hooks/useAvailableSTs.ts
import { useState, useEffect } from 'react'
import { apiGet } from '../../../api/client'
import type { AvailableST } from '../types'

export function useAvailableSTs(date: Date, unassignedOnly: boolean) {
  const [sts, setSTs]         = useState<AvailableST[]>([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const dateStr = date.toISOString().slice(0, 10)

  useEffect(() => {
    setLoading(true)
    apiGet<AvailableST[]>(
      `/transport/pallets/available?date=${dateStr}&unassigned_only=${unassignedOnly}`
    ).then(data => setSTs(data)).finally(() => setLoading(false))
  }, [dateStr, unassignedOnly])

  const toggle = (stNumber: string) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(stNumber) ? next.delete(stNumber) : next.add(stNumber)
      return next
    })
  }

  const clearSelection = () => setSelected(new Set())

  // Live-итог выбранных
  const summary = sts
    .filter(s => selected.has(s.st_number))
    .reduce((acc, s) => ({
      pallets: acc.pallets + s.pallets_count,
      weight:  acc.weight  + s.weight_kg,
      volume:  acc.volume  + s.volume_m3,
    }), { pallets: 0, weight: 0, volume: 0 })

  return { sts, loading, selected, toggle, clearSelection, summary, reload: () => {} }
}
```

### 4.5 AvailableOrdersTable.tsx (ключевые части)

```tsx
// src/components/Transport/assignment/AvailableOrdersTable.tsx
import React, { useMemo } from 'react'
import { Table, Checkbox, Input, Select, Tag } from 'antd'
import type { AvailableST } from '../types'

const RAION_COLORS: Record<string, string> = {}
const PALETTE = ['#1890ff','#52c41a','#faad14','#f5222d',
                  '#722ed1','#13c2c2','#eb2f96','#fa8c16']

function getRaionColor(raion: string): string {
  if (!RAION_COLORS[raion]) {
    const idx = Object.keys(RAION_COLORS).length % PALETTE.length
    RAION_COLORS[raion] = PALETTE[idx]
  }
  return RAION_COLORS[raion]
}

interface Props {
  sts: AvailableST[]
  selected: Set<string>
  onToggle: (st: string) => void
  onToggleAll: (all: boolean) => void
  loading: boolean
}

export default function AvailableOrdersTable({
  sts, selected, onToggle, onToggleAll, loading
}: Props) {
  const columns = [
    {
      title: <Checkbox
        checked={selected.size === sts.length && sts.length > 0}
        indeterminate={selected.size > 0 && selected.size < sts.length}
        onChange={e => onToggleAll(e.target.checked)}
      />,
      width: 40,
      render: (_: any, r: AvailableST) => (
        <Checkbox
          checked={selected.has(r.st_number)}
          onChange={() => onToggle(r.st_number)}
        />
      ),
    },
    {
      title: 'Р',  // Район
      width: 8,
      render: (_: any, r: AvailableST) => r.raion ? (
        <div style={{
          width: 6, height: 24, borderRadius: 3,
          background: getRaionColor(r.raion)
        }} title={r.raion} />
      ) : null,
    },
    {
      title: 'Адрес',
      dataIndex: 'addr',
      ellipsis: true,
      render: (v: string, r: AvailableST) => (
        <span>
          {v}
          {r.needs_hydro_board && (
            <Tag color="orange" style={{ marginLeft: 4, fontSize: 10 }}>ГБ</Tag>
          )}
        </span>
      )
    },
    { title: 'СТ',   dataIndex: 'st_number', width: 70 },
    { title: 'Палл', dataIndex: 'pallets_count', width: 55, align: 'right' as const },
    { title: 'Вес',  dataIndex: 'weight_kg', width: 65, align: 'right' as const,
      render: (v: number) => v.toFixed(0) },
    {
      title: 'Пров',
      width: 55,
      dataIndex: 'verify_pct',
      render: (v: number) => (
        <span style={{ color: v < 100 ? '#faad14' : '#52c41a' }}>{v}%</span>
      )
    },
    {
      title: 'Окно',
      width: 90,
      render: (_: any, r: AvailableST) =>
        r.delivery_time_from
          ? `${r.delivery_time_from}–${r.delivery_time_to}`
          : '—'
    },
  ]

  return (
    <Table
      size="small"
      dataSource={sts}
      rowKey="st_number"
      columns={columns}
      loading={loading}
      pagination={false}
      scroll={{ y: 'calc(100vh - 280px)' }}
      rowClassName={(r) =>
        selected.has(r.st_number) ? 'row-selected' : ''
      }
    />
  )
}
```

### 4.6 TransportTaskCard.tsx

```tsx
// src/components/Transport/assignment/TransportTaskCard.tsx
import React from 'react'
import { Card, Progress, Space, Tag, Tooltip } from 'antd'
import { WarningOutlined } from '@ant-design/icons'
import type { TransportTask } from '../types'

const CONDITION_COLOR: Record<string, string> = {
  CREATED: 'default', PLANNED: 'processing',
  DOCK_RESERVED: 'cyan', LOADING: 'blue', DISPATCHED: 'green',
}

interface Props {
  task: TransportTask
  selected: boolean
  onClick: () => void
}

export default function TransportTaskCard({ task, selected, onClick }: Props) {
  const pallPct = task.pallets_capacity
    ? Math.min((task.pallets_count / task.pallets_capacity) * 100, 110)
    : null
  const wtPct = task.weight_capacity && task.weight_kg
    ? Math.min((task.weight_kg / task.weight_capacity) * 100, 110)
    : null

  const overloaded = (pallPct && pallPct > 100) || (wtPct && wtPct > 100)

  return (
    <Card
      size="small"
      hoverable
      onClick={onClick}
      style={{
        marginBottom: 8,
        border: selected ? '2px solid #1890ff' : '1px solid #f0f0f0',
        cursor: 'pointer',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <Space>
          <span style={{ fontWeight: 600 }}>Рейс #{task.id}</span>
          <Tag color={CONDITION_COLOR[task.condition]}>{task.condition}</Tag>
        </Space>
        {overloaded && <Tooltip title="Перегруз"><WarningOutlined style={{ color: '#f5222d' }} /></Tooltip>}
      </div>

      <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>
        {task.vehicle?.num ?? '—'} · {task.driver?.full_name ?? 'водитель не назначен'}
      </div>

      {pallPct !== null && (
        <div>
          <div style={{ fontSize: 11, color: '#999' }}>
            Палл {task.pallets_count}/{task.pallets_capacity}
          </div>
          <Progress
            percent={Math.min(pallPct, 100)}
            showInfo={false}
            size="small"
            status={pallPct > 100 ? 'exception' : 'normal'}
          />
        </div>
      )}

      {wtPct !== null && (
        <div>
          <div style={{ fontSize: 11, color: '#999' }}>
            Вес {task.weight_kg.toFixed(0)} / {task.weight_capacity} кг
          </div>
          <Progress
            percent={Math.min(wtPct, 100)}
            showInfo={false}
            size="small"
            status={wtPct > 100 ? 'exception' : 'normal'}
          />
        </div>
      )}

      {(task.distance_km || task.estimated_cost) && (
        <div style={{ fontSize: 11, marginTop: 4, color: '#555' }}>
          {task.distance_km && `${task.distance_km.toFixed(1)} км`}
          {task.estimated_hours && ` · ~${task.estimated_hours.toFixed(1)} ч`}
          {task.estimated_cost && ` · ${Math.round(task.estimated_cost).toLocaleString()} ₽`}
        </div>
      )}

      {task.dock && (
        <div style={{ fontSize: 11, color: '#1890ff', marginTop: 2 }}>
          Дока {task.dock}
          {task.dock_from && ` ${new Date(task.dock_from).toLocaleTimeString('ru', {hour:'2-digit',minute:'2-digit'})}–${new Date(task.dock_to!).toLocaleTimeString('ru', {hour:'2-digit',minute:'2-digit'})}`}
        </div>
      )}
    </Card>
  )
}
```

### 4.7 AssignmentModeView.tsx (скелет)

```tsx
// src/components/Transport/assignment/AssignmentModeView.tsx
import React, { useState } from 'react'
import { Button, Space, message, Modal } from 'antd'
import { PlusOutlined, ArrowRightOutlined, ThunderboltOutlined } from '@ant-design/icons'
import TransportTaskCard from './TransportTaskCard'
import AvailableOrdersTable from './AvailableOrdersTable'
import TaskPalletsTable from './TaskPalletsTable'
import AssignmentSummaryBar from '../shared/AssignmentSummaryBar'
import { useTransportTasks } from '../hooks/useTransportTasks'
import { useAvailableSTs } from '../hooks/useAvailableSTs'
import { useCapacityWarnings } from '../hooks/useCapacityWarnings'

const USER_ID = 'DISPATCHER'  // заменить на auth context

interface Props { date: Date }

export default function AssignmentModeView({ date }: Props) {
  const { tasks, loading: tLoading, selectedId, setSelectedId,
          reload, assignSTs, unassignST, createTask }
    = useTransportTasks(date)

  const { sts, loading: sLoading, selected, toggle,
          clearSelection, summary }
    = useAvailableSTs(date, true)

  const selectedTask = tasks.find(t => t.id === selectedId) ?? null
  const warnings = useCapacityWarnings(selectedTask, selected, sts)

  const handleAssign = async () => {
    if (!selectedId || selected.size === 0) return
    const warns = await assignSTs(selectedId, Array.from(selected), USER_ID)
    clearSelection()
    if (warns.length) message.warning(`Предупреждения: ${warns.join(', ')}`)
  }

  const handleCreate = async () => {
    if (selected.size === 0) return
    const id = await createTask('15', Array.from(selected), USER_ID)
    clearSelection()
    message.success(`Рейс #${id} создан`)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gridTemplateRows: '1fr auto', height: '100%', gap: 0 }}>

      {/* Левая колонка — рейсы */}
      <div style={{ borderRight: '1px solid #f0f0f0', padding: 8, overflowY: 'auto' }}>
        <Button icon={<PlusOutlined />} type="dashed" block style={{ marginBottom: 8 }}
                onClick={handleCreate} disabled={selected.size === 0}>
          Создать рейс
        </Button>
        {tasks.map(t => (
          <TransportTaskCard
            key={t.id}
            task={t}
            selected={t.id === selectedId}
            onClick={() => setSelectedId(t.id)}
          />
        ))}
      </div>

      {/* Правая колонка — СТ + состав */}
      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* Таблица доступных СТ */}
        <div style={{ flex: 1, overflow: 'hidden', padding: '8px 8px 0' }}>
          <AvailableOrdersTable
            sts={sts}
            selected={selected}
            onToggle={toggle}
            onToggleAll={(all) => { /* toggle all */ }}
            loading={sLoading}
          />
        </div>

        {/* Итог + кнопка добавить */}
        <div style={{ padding: '8px', borderTop: '1px solid #f0f0f0', background: '#fafafa' }}>
          <Space>
            <AssignmentSummaryBar summary={summary} />
            <Button
              type="primary"
              icon={<ArrowRightOutlined />}
              disabled={!selectedId || selected.size === 0}
              onClick={handleAssign}
            >
              В рейс #{selectedId}
            </Button>
          </Space>
        </div>

        {/* Состав выбранного рейса */}
        {selectedTask && (
          <TaskPalletsTable
            taskId={selectedTask.id}
            onUnassign={(st) => unassignST(selectedTask.id, st, USER_ID)}
          />
        )}
      </div>
    </div>
  )
}
```

---

## 5. Фаза 3: React — полу-авто

### 5.1 PlanningModeView.tsx (скелет)

```tsx
// src/components/Transport/planning/PlanningModeView.tsx
import React from 'react'
import { Row, Col, Card, Statistic, Progress } from 'antd'
import PlanningMap from './PlanningMap'
import { useDaySummary } from '../hooks/useDaySummary'
import { useAvailableSTs } from '../hooks/useAvailableSTs'

interface Props { date: Date }

export default function PlanningModeView({ date }: Props) {
  const summary = useDaySummary(date)
  const { sts } = useAvailableSTs(date, false)

  const coveragePct = summary
    ? Math.min(
        (summary.total_vehicle_capacity /
         Math.max(summary.unassigned_pallets, 1)) * 100, 100
      )
    : 0

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Сводка дня */}
      {summary && (
        <Row gutter={16} style={{ padding: '8px 16px', background: '#fff', borderBottom: '1px solid #f0f0f0' }}>
          <Col><Statistic title="СТ к отгрузке" value={summary.total_sts} /></Col>
          <Col><Statistic title="Паллет" value={summary.total_pallets} /></Col>
          <Col><Statistic title="Не распределено" value={summary.unassigned_pallets} /></Col>
          <Col><Statistic title="Машин" value={summary.available_vehicles} /></Col>
          <Col>
            <div>Покрытие</div>
            <Progress
              percent={Math.round(coveragePct)}
              status={summary.coverage_ok ? 'normal' : 'exception'}
              style={{ width: 120 }}
            />
          </Col>
        </Row>
      )}

      {/* Карта */}
      <div style={{ flex: 1 }}>
        <PlanningMap sts={sts} />
      </div>
    </div>
  )
}
```

### 5.2 PlanningMap.tsx

```tsx
// src/components/Transport/planning/PlanningMap.tsx
// Требует: npm install leaflet react-leaflet @types/leaflet

import React, { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { AvailableST } from '../types'

const RAION_PALETTE = ['#1890ff','#52c41a','#faad14','#f5222d','#722ed1','#13c2c2']
const raionColorMap: Record<string, string> = {}
let colorIdx = 0
function getColor(raion: string) {
  if (!raionColorMap[raion]) {
    raionColorMap[raion] = RAION_PALETTE[colorIdx++ % RAION_PALETTE.length]
  }
  return raionColorMap[raion]
}

interface Props {
  sts: AvailableST[]
  routeCoords?: [number, number][]  // для отрисовки polyline рейса
}

export default function PlanningMap({ sts, routeCoords }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.CircleMarker[]>([])
  const polylineRef = useRef<L.Polyline | null>(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    mapRef.current = L.map(containerRef.current).setView([55.75, 37.61], 10)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(mapRef.current)
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    markersRef.current.forEach(m => m.remove())
    markersRef.current = []

    sts.forEach(st => {
      if (!st.lat || !st.lon) return
      const color = getColor(st.raion ?? '—')
      const marker = L.circleMarker([st.lat, st.lon], {
        radius: 5 + Math.min(st.pallets_count, 5),
        fillColor: color,
        color: '#fff',
        weight: 1,
        opacity: st.transtask_id ? 0.4 : 1,
        fillOpacity: st.transtask_id ? 0.3 : 0.85,
      })
      marker.bindPopup(
        `<b>${st.addr}</b><br/>СТ: ${st.st_number}<br/>` +
        `${st.pallets_count} палл · ${st.weight_kg.toFixed(0)} кг<br/>` +
        `Район: ${st.raion ?? '—'}`
      )
      marker.addTo(map)
      markersRef.current.push(marker)
    })
  }, [sts])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    if (polylineRef.current) { polylineRef.current.remove(); polylineRef.current = null }
    if (routeCoords && routeCoords.length > 1) {
      polylineRef.current = L.polyline(routeCoords, { color: '#1890ff', weight: 3 })
        .addTo(map)
    }
  }, [routeCoords])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}
```

### 5.3 useRouteMetrics.ts (Haversine на клиенте)

```typescript
// src/components/Transport/hooks/useRouteMetrics.ts
import { useMemo } from 'react'
import type { TaskPalletRow } from '../types'

const AVG_SPEED = 40  // км/ч
const DEPOT = { lat: 55.75, lon: 37.61 }  // координаты склада — вынести в конфиг

function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat/2)**2 +
    Math.cos(lat1 * Math.PI/180) * Math.cos(lat2 * Math.PI/180) * Math.sin(dLon/2)**2
  return R * 2 * Math.asin(Math.sqrt(a))
}

export function useRouteMetrics(pallets: TaskPalletRow[]) {
  return useMemo(() => {
    const sorted = [...pallets]
      .filter(p => p.lat && p.lon)
      .sort((a, b) => a.ord - b.ord)

    if (sorted.length === 0) return { distanceKm: 0, estimatedHours: 0 }

    let dist = haversine(DEPOT.lat, DEPOT.lon, sorted[0].lat!, sorted[0].lon!)
    for (let i = 0; i < sorted.length - 1; i++) {
      dist += haversine(sorted[i].lat!, sorted[i].lon!,
                        sorted[i+1].lat!, sorted[i+1].lon!)
    }
    dist += haversine(sorted[sorted.length-1].lat!, sorted[sorted.length-1].lon!,
                      DEPOT.lat, DEPOT.lon)

    const serviceMins = sorted.reduce((s, p) => s + (p.service_min ?? 15), 0)
    const hours = dist / AVG_SPEED + serviceMins / 60

    return { distanceKm: Math.round(dist * 10) / 10, estimatedHours: Math.round(hours * 10) / 10 }
  }, [pallets])
}
```

---

## 6. Фаза 4: OSRM

### 6.1 Развёртывание

```bash
# Скачать выгрузку России (~3 ГБ)
wget https://download.geofabrik.de/russia-latest.osm.pbf -P /data/osrm/

# Предобработка (1 раз, ~20–40 мин)
docker run -t -v /data/osrm:/data osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/russia-latest.osm.pbf
docker run -t -v /data/osrm:/data osrm/osrm-backend \
  osrm-partition /data/russia-latest.osrm
docker run -t -v /data/osrm:/data osrm/osrm-backend \
  osrm-customize /data/russia-latest.osrm

# Запуск
docker run -d --name osrm -p 5000:5000 -v /data/osrm:/data \
  osrm/osrm-backend osrm-routed --algorithm mld /data/russia-latest.osrm

# Проверка
curl "http://localhost:5000/table/v1/driving/37.61,55.75;37.65,55.78?annotations=duration,distance"
```

### 6.2 vrp_matrix_worker.py

```python
# api/wms_api_server/app/workers/vrp_matrix_worker.py

import httpx
import cx_Oracle
import itertools
import logging
from datetime import date, timedelta

OSRM_URL    = "http://localhost:5000"
BATCH_SIZE  = 50
STALE_DAYS  = 30

log = logging.getLogger(__name__)


def get_all_active_addrs(conn) -> list[dict]:
    cur = conn.cursor()
    cur.execute("""
        SELECT ADDR, SHIROTA, DOLGOTA
          FROM RABAEV.RRL_ADDR
         WHERE SHIROTA IS NOT NULL AND DOLGOTA IS NOT NULL
           AND (DELETED IS NULL OR DELETED <> 1)
    """)
    return [{"addr": r[0], "lat": float(r[1]), "lon": float(r[2])}
            for r in cur.fetchall()]


def get_missing_pairs(conn, addrs: list[dict]) -> list[tuple]:
    """Пары, которых нет в кэше или устарели."""
    codes = {a["addr"] for a in addrs}
    cutoff = date.today() - timedelta(days=STALE_DAYS)
    cur = conn.cursor()
    cur.execute("""
        SELECT ADDR_FROM, ADDR_TO FROM RABAEV.RRL_ADDR_DISTANCE_MATRIX
         WHERE CALC_DATE >= :1
    """, [cutoff])
    existing = {(r[0], r[1]) for r in cur.fetchall()}
    all_pairs = {(a, b) for a, b in itertools.product(codes, codes) if a != b}
    return list(all_pairs - existing)


def fetch_matrix_batch(nodes: list[dict]) -> dict:
    """OSRM Table API для batch узлов."""
    coords = ";".join(f"{n['lon']},{n['lat']}" for n in nodes)
    resp = httpx.get(
        f"{OSRM_URL}/table/v1/driving/{coords}",
        params={"annotations": "duration,distance"},
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "durations": data["durations"],
        "distances": data["distances"],
    }


def save_batch(conn, nodes: list[dict], matrix: dict):
    cur = conn.cursor()
    rows = []
    for i, src in enumerate(nodes):
        for j, dst in enumerate(nodes):
            if i == j:
                continue
            dist = matrix["distances"][i][j]
            dur  = matrix["durations"][i][j]
            if dist is not None and dur is not None:
                rows.append((src["addr"], dst["addr"],
                             int(dist), int(dur)))
    cur.executemany("""
        MERGE INTO RABAEV.RRL_ADDR_DISTANCE_MATRIX D
          USING (SELECT :1 AF, :2 AT FROM DUAL) S
             ON (D.ADDR_FROM = S.AF AND D.ADDR_TO = S.AT)
         WHEN MATCHED THEN
           UPDATE SET DIST_METERS=:3, DURATION_SEC=:4, CALC_DATE=SYSDATE
         WHEN NOT MATCHED THEN
           INSERT (ADDR_FROM,ADDR_TO,DIST_METERS,DURATION_SEC)
           VALUES (:1, :2, :3, :4)
    """, rows)
    conn.commit()


def run(conn):
    log.info("VRP matrix sync started")
    addrs = get_all_active_addrs(conn)
    missing = get_missing_pairs(conn, addrs)
    log.info(f"Missing pairs: {len(missing)}")

    addr_map = {a["addr"]: a for a in addrs}
    # Разбиваем на батчи по BATCH_SIZE уникальных адресов
    unique_addrs_needed = list({a for pair in missing for a in pair})

    for i in range(0, len(unique_addrs_needed), BATCH_SIZE):
        batch_addrs = unique_addrs_needed[i:i+BATCH_SIZE]
        nodes = [addr_map[a] for a in batch_addrs if a in addr_map]
        try:
            matrix = fetch_matrix_batch(nodes)
            save_batch(conn, nodes, matrix)
            log.info(f"Saved batch {i//BATCH_SIZE + 1}")
        except Exception as e:
            log.error(f"Batch {i} failed: {e}")

    log.info("VRP matrix sync complete")


if __name__ == "__main__":
    import os
    dsn = cx_Oracle.makedsn(
        os.environ["ORACLE_HOST"], os.environ["ORACLE_PORT"],
        service_name=os.environ["ORACLE_SERVICE"]
    )
    conn = cx_Oracle.connect(os.environ["ORACLE_USER"],
                              os.environ["ORACLE_PASS"], dsn)
    run(conn)
    conn.close()
```

---

## 7. Фаза 5: VRP-решатели

### 7.1 vrp_service.py — общая структура

```python
# api/wms_api_server/app/services/vrp_service.py

import math
import json
from dataclasses import dataclass
from typing import Optional
import cx_Oracle


@dataclass
class AddrNode:
    addr: str
    lat: float
    lon: float
    pallets: int
    weight_kg: float
    service_min: int = 15
    tw_from: Optional[int] = None  # минут от 00:00
    tw_to:   Optional[int] = None

@dataclass
class Vehicle:
    id: int
    num: str
    pallets_capacity: int
    weight_capacity: Optional[float]

@dataclass
class RouteTask:
    vehicle: Vehicle
    nodes: list[AddrNode]  # в порядке объезда
    total_km: float
    estimated_hours: float


def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    d1 = math.radians(lat2-lat1)
    d2 = math.radians(lon2-lon1)
    a = math.sin(d1/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(d2/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def nearest_neighbour_tsp(
    nodes: list[dict],  # [{"st_number","lat","lon","ord"}]
    depot_lat: float,
    depot_lon: float
) -> list[dict]:
    """Nearest-neighbour TSP. Возвращает [{st_number, new_ord, addr}]."""
    if not nodes:
        return []
    unvisited = list(nodes)
    result = []
    cur_lat, cur_lon = depot_lat, depot_lon

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda n: haversine(cur_lat, cur_lon, n['lat'], n['lon'])
        )
        unvisited.remove(nearest)
        result.append(nearest)
        cur_lat, cur_lon = nearest['lat'], nearest['lon']

    return [
        {"st_number": n["st_number"], "new_ord": i+1}
        for i, n in enumerate(result)
    ]
```

### 7.2 Clarke-Wright savings

```python
def clarke_wright(
    nodes: list[AddrNode],
    vehicles: list[Vehicle],
    depot_lat: float,
    depot_lon: float,
    dist_matrix: Optional[dict] = None
) -> list[RouteTask]:
    """Clarke-Wright Savings Algorithm."""
    def dist(n1, n2):
        key = (n1.addr, n2.addr)
        if dist_matrix and key in dist_matrix:
            return dist_matrix[key]["dist_meters"] / 1000.0
        return haversine(n1.lat, n1.lon, n2.lat, n2.lon)

    def dist_depot(n):
        return haversine(depot_lat, depot_lon, n.lat, n.lon)

    # Savings: s(i,j) = d(0,i) + d(0,j) - d(i,j)
    savings = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            s = dist_depot(nodes[i]) + dist_depot(nodes[j]) - dist(nodes[i], nodes[j])
            savings.append((s, i, j))
    savings.sort(key=lambda x: -x[0])

    # Инициализация: каждый узел — отдельный маршрут
    routes: list[list[int]] = [[i] for i in range(len(nodes))]
    node_route: dict[int, int] = {i: i for i in range(len(nodes))}

    def route_pallets(r_idx: int) -> int:
        return sum(nodes[i].pallets for i in routes[r_idx])

    cap = max((v.pallets_capacity for v in vehicles), default=20)

    for _, i, j in savings:
        ri, rj = node_route.get(i), node_route.get(j)
        if ri is None or rj is None or ri == rj:
            continue
        if route_pallets(ri) + route_pallets(rj) <= cap:
            # Merge: rj → ri
            routes[ri].extend(routes[rj])
            for n in routes[rj]:
                node_route[n] = ri
            routes[rj] = []

    result_routes = [r for r in routes if r]

    # NN-сортировка внутри каждого маршрута
    final = []
    for r_nodes_idx in result_routes:
        r_nodes = [nodes[i] for i in r_nodes_idx]
        sorted_nodes = _nn_sort_nodes(r_nodes, depot_lat, depot_lon)
        km = _route_km(sorted_nodes, depot_lat, depot_lon)
        hours = km / 40.0 + sum(n.service_min for n in sorted_nodes) / 60.0
        veh = vehicles[len(final) % len(vehicles)] if vehicles else None
        final.append(RouteTask(vehicle=veh, nodes=sorted_nodes,
                               total_km=km, estimated_hours=hours))
    return final


def _nn_sort_nodes(nodes: list[AddrNode], dep_lat, dep_lon) -> list[AddrNode]:
    unvis = list(nodes)
    result = []
    clat, clon = dep_lat, dep_lon
    while unvis:
        nxt = min(unvis, key=lambda n: haversine(clat, clon, n.lat, n.lon))
        unvis.remove(nxt)
        result.append(nxt)
        clat, clon = nxt.lat, nxt.lon
    return result


def _route_km(nodes: list[AddrNode], dep_lat, dep_lon) -> float:
    if not nodes:
        return 0.0
    pts = [(dep_lat, dep_lon)] + [(n.lat, n.lon) for n in nodes] + [(dep_lat, dep_lon)]
    return sum(haversine(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1])
               for i in range(len(pts)-1))
```

### 7.3 OR-Tools VRP

```python
def solve_ortools(
    nodes: list[AddrNode],
    vehicles: list[Vehicle],
    depot_lat: float,
    depot_lon: float,
    dist_matrix: Optional[dict],
    time_limit_sec: int = 10
) -> list[RouteTask]:
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp

    N = len(nodes) + 1  # +1 depot at index 0
    K = len(vehicles)

    def dist_m(i, j) -> int:
        if i == 0:
            n = nodes[j-1]
            return int(haversine(depot_lat, depot_lon, n.lat, n.lon) * 1000)
        if j == 0:
            n = nodes[i-1]
            return int(haversine(n.lat, n.lon, depot_lat, depot_lon) * 1000)
        a, b = nodes[i-1], nodes[j-1]
        key = (a.addr, b.addr)
        if dist_matrix and key in dist_matrix:
            return int(dist_matrix[key]["dist_meters"])
        return int(haversine(a.lat, a.lon, b.lat, b.lon) * 1000)

    manager = pywrapcp.RoutingIndexManager(N, K, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def dist_cb(from_idx, to_idx):
        return dist_m(manager.IndexToNode(from_idx),
                      manager.IndexToNode(to_idx))
    cb_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(cb_idx)

    # Capacity constraint
    def demand_cb(from_idx):
        node = manager.IndexToNode(from_idx)
        return nodes[node-1].pallets if node > 0 else 0
    dem_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(
        dem_idx, 0,
        [v.pallets_capacity for v in vehicles],
        True, 'Capacity'
    )

    # Time windows (если заданы)
    service_times_defined = any(n.tw_from for n in nodes)
    if service_times_defined:
        def time_cb(from_idx, to_idx):
            fm = manager.IndexToNode(from_idx)
            to = manager.IndexToNode(to_idx)
            travel = dist_m(fm, to) // 1000 // 40 * 60  # мин
            service = nodes[fm-1].service_min if fm > 0 else 0
            return travel + service
        t_idx = routing.RegisterTransitCallback(time_cb)
        routing.AddDimension(t_idx, 30, 24*60, False, 'Time')
        time_dim = routing.GetDimensionOrDie('Time')
        for i, n in enumerate(nodes):
            if n.tw_from and n.tw_to:
                idx = manager.NodeToIndex(i+1)
                time_dim.CumulVar(idx).SetRange(n.tw_from, n.tw_to)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.seconds = time_limit_sec

    solution = routing.SolveWithParameters(params)
    if not solution:
        return []

    result = []
    for v_idx in range(K):
        route_nodes = []
        idx = routing.Start(v_idx)
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            if node > 0:
                route_nodes.append(nodes[node-1])
            idx = solution.Value(routing.NextVar(idx))
        if route_nodes:
            km = _route_km(route_nodes, depot_lat, depot_lon)
            hours = km / 40.0 + sum(n.service_min for n in route_nodes) / 60.0
            result.append(RouteTask(vehicle=vehicles[v_idx],
                                    nodes=route_nodes,
                                    total_km=km, estimated_hours=hours))
    return result
```

### 7.4 Шаблонный движок

```python
def jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def find_best_template(
    dow: int,
    transtype: str,
    addr_set: set,
    min_similarity: float,
    conn
) -> Optional[dict]:
    cur = conn.cursor()
    cur.execute("""
        SELECT ID, ADDR_SIGNATURE, ADDR_LIST, TOTAL_KM, TOTAL_HOURS, USAGE_COUNT
          FROM RABAEV.RRL_TT_ROUTE_TEMPLATE
         WHERE DOW = :1 AND TRANSTYPE = :2
           AND USAGE_COUNT >= 3
         ORDER BY QUALITY_SCORE DESC, USAGE_COUNT DESC
    """, [dow, transtype])
    best = None
    best_score = 0.0
    for row in cur.fetchall():
        tmpl_addrs = set(row[1].split(',')) if row[1] else set()
        score = jaccard(addr_set, tmpl_addrs)
        if score > best_score:
            best_score = score
            best = {"id": row[0], "similarity": score,
                    "addr_list": json.loads(row[2]) if row[2] else [],
                    "total_km": row[3], "total_hours": row[4],
                    "usage_count": row[5]}
    return best if best and best_score >= min_similarity else None


def save_template(dow: int, transtype: str,
                  route: RouteTask, conn):
    addr_sig = ','.join(sorted(n.addr for n in route.nodes))
    addr_list = json.dumps([
        {"addr": n.addr, "ord": i+1,
         "avg_pallets": n.pallets, "lat": n.lat, "lon": n.lon}
        for i, n in enumerate(route.nodes)
    ])
    existing = find_best_template(dow, transtype,
                                   set(n.addr for n in route.nodes),
                                   0.85, conn)
    cur = conn.cursor()
    if existing:
        cur.execute("""
            UPDATE RABAEV.RRL_TT_ROUTE_TEMPLATE
               SET USAGE_COUNT = USAGE_COUNT + 1,
                   LAST_USED   = SYSDATE,
                   TOTAL_KM    = :1,
                   TOTAL_HOURS = :2
             WHERE ID = :3
        """, [route.total_km, route.estimated_hours, existing["id"]])
    else:
        cur.execute("""
            INSERT INTO RABAEV.RRL_TT_ROUTE_TEMPLATE
              (DOW, TRANSTYPE, ADDR_SIGNATURE, ADDR_LIST, TOTAL_KM, TOTAL_HOURS, USAGE_COUNT)
            VALUES (:1,:2,:3,:4,:5,:6, 1)
        """, [dow, transtype, addr_sig, addr_list,
              route.total_km, route.estimated_hours])
    conn.commit()
```

### 7.5 Эндпоинты авто-плана

```python
# В transport.py — добавить:

from ..services.vrp_service import (
    AddrNode, Vehicle, clarke_wright, solve_ortools,
    find_best_template, save_template
)
import asyncio

@router.post("/planning/auto-plan")
async def auto_plan(
    date: date = Query(...),
    ortools_time_limit_sec: int = Query(default=10),
    conn=Depends(get_oracle_conn)
):
    # 1. Загрузить данные
    sts = svc.get_available_sts(date, True, None, None, conn)
    vehicles = _load_vehicles(conn)
    dist_matrix = _load_dist_matrix(conn, [s.addr for s in sts])

    depot_lat, depot_lon = 55.75, 37.61  # из конфига
    nodes = [AddrNode(
        addr=s.addr, lat=s.lat or 0, lon=s.lon or 0,
        pallets=s.pallets_count, weight_kg=s.weight_kg,
        service_min=s.service_min,
    ) for s in sts if s.lat and s.lon]

    dow = date.weekday() + 1  # 1=пн
    addrs_set = {n.addr for n in nodes}

    variants = []

    # 2. Шаблон (< 50 мс)
    tmpl = find_best_template(dow, '0', addrs_set, 0.85, conn)
    if tmpl:
        variants.append({
            "solver": "template",
            "similarity": tmpl["similarity"],
            "route": tmpl["addr_list"],
            "total_km": tmpl["total_km"],
            "estimated_hours": tmpl["total_hours"],
            "handles_time_windows": False,
        })

    # 3. OR-Tools + Clarke-Wright параллельно
    async def run_ortools():
        return solve_ortools(nodes, vehicles, depot_lat, depot_lon,
                             dist_matrix, ortools_time_limit_sec)

    async def run_cw():
        return clarke_wright(nodes, vehicles, depot_lat, depot_lon, dist_matrix)

    ortools_res, cw_res = await asyncio.gather(
        asyncio.to_thread(solve_ortools, nodes, vehicles,
                          depot_lat, depot_lon, dist_matrix, ortools_time_limit_sec),
        asyncio.to_thread(clarke_wright, nodes, vehicles,
                          depot_lat, depot_lon, dist_matrix),
    )

    for label, res, handles_tw in [
        ("ortools", ortools_res, True),
        ("clarke_wright", cw_res, False),
    ]:
        if res:
            variants.append({
                "solver": label,
                "routes": [
                    {"nodes": [n.addr for n in r.nodes],
                     "total_km": r.total_km,
                     "vehicle": r.vehicle.num if r.vehicle else None}
                    for r in res
                ],
                "total_km": sum(r.total_km for r in res),
                "estimated_hours": max((r.estimated_hours for r in res), default=0),
                "handles_time_windows": handles_tw,
            })

    # Сессия для аудита
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO RABAEV.RRL_TT_AUTO_PLAN_SESSION
          (PLAN_DATE, INPUT_ST_COUNT, RESULT_TASK_COUNT, SESSION_JSON)
        VALUES (:1, :2, :3, :4)
        RETURNING ID INTO :5
    """, [date, len(nodes), len(variants[0].get("routes",[1])),
          json.dumps({"variants": len(variants)}),
          cur.var(cx_Oracle.NUMBER)])
    session_id = cur.bindvars[-1].getvalue()
    conn.commit()

    return {"session_id": session_id, "variants": variants,
            "uncovered_count": len(sts) - len(nodes)}


@router.post("/planning/accept")
def accept_plan(
    session_id: int = Query(...),
    variant_idx: int = Query(default=0),
    user_id: str = Query(...),
    conn=Depends(get_oracle_conn)
):
    # Принять выбранный вариант: создать рейсы в Oracle
    # (реализация зависит от формата variant)
    # Обновить сессию
    conn.cursor().execute("""
        UPDATE RABAEV.RRL_TT_AUTO_PLAN_SESSION
           SET ACCEPTED_BY = :1, ACCEPTED_AT = SYSDATE
         WHERE ID = :2
    """, [user_id, session_id])
    conn.commit()
    return {"ok": True}
```

---

## 8. Фаза 6: Attention Model

### 8.1 Архитектура (минимальная реализация)

```python
# api/wms_api_server/app/ml/attention_vrp.py
# Упрощённый Attention Model (Kool et al. ICLR 2019)

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

D_MODEL = 128
N_HEADS  = 8
N_LAYERS = 3


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.mha = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, kv=None):
        kv = kv if kv is not None else x
        out, _ = self.mha(x, kv, kv)
        return self.norm(x + out)


class Encoder(nn.Module):
    def __init__(self, in_features=3):  # [x, y, demand]
        super().__init__()
        self.embed = nn.Linear(in_features, D_MODEL)
        self.layers = nn.ModuleList(
            [MultiHeadAttention(D_MODEL, N_HEADS) for _ in range(N_LAYERS)]
        )

    def forward(self, x):        # x: (B, N, 3)
        h = self.embed(x)
        for layer in self.layers:
            h = layer(h)
        return h                  # (B, N, D_MODEL)


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.attn = MultiHeadAttention(D_MODEL, N_HEADS)
        self.pointer = nn.Linear(D_MODEL, 1)

    def forward(self, ctx, mem, mask):
        ctx = self.attn(ctx.unsqueeze(1), mem).squeeze(1)
        logits = self.pointer(mem).squeeze(-1)
        logits[mask] = float('-inf')
        return logits              # (B, N)


class AttentionVRP(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()
        self.context_proj = nn.Linear(D_MODEL * 2, D_MODEL)

    def forward(self, coords, demands, capacity):
        """
        coords:   (B, N, 2)
        demands:  (B, N)
        capacity: scalar
        """
        B, N, _ = coords.shape
        x = torch.cat([coords, demands.unsqueeze(-1)], dim=-1)  # (B,N,3)
        h = self.encoder(x)                                       # (B,N,D)

        routes = []
        remaining = demands.clone().float()   # (B,N)
        cur_load = torch.zeros(B)             # (B,)
        visited = torch.zeros(B, N, dtype=torch.bool)
        cur_node = torch.zeros(B, D_MODEL)    # depot context

        for step in range(N):
            mask = visited | (remaining > (capacity - cur_load.unsqueeze(1)))
            if mask.all():
                break  # все посещены или не помещаются

            graph_ctx = h.mean(1)                    # (B,D)
            ctx = self.context_proj(
                torch.cat([graph_ctx, cur_node], dim=-1)
            )                                        # (B,D)
            logits = self.decoder(ctx, h, mask)      # (B,N)
            probs  = F.softmax(logits, dim=-1)       # (B,N)

            # Greedy / sample
            node_idx = probs.argmax(dim=-1)           # (B,)
            routes.append(node_idx)

            for b in range(B):
                ni = node_idx[b].item()
                visited[b, ni] = True
                cur_load[b] += demands[b, ni]
                cur_node[b] = h[b, ni]

        return torch.stack(routes, dim=1)  # (B, steps)


# Singleton — загружается один раз
_model: Optional[AttentionVRP] = None
MODEL_PATH = "models/attention_vrp.pt"


def get_model() -> AttentionVRP:
    global _model
    if _model is None:
        _model = AttentionVRP()
        try:
            state = torch.load(MODEL_PATH, map_location='cpu')
            _model.load_state_dict(state)
            _model.eval()
        except FileNotFoundError:
            pass  # не обучена ещё — вернёт случайные маршруты
    return _model


def solve_attention(
    nodes: list,       # list[AddrNode]
    vehicles: list,
    depot_lat: float,
    depot_lon: float,
) -> list:
    model = get_model()
    if not nodes:
        return []

    # Нормализация координат
    lats = [n.lat for n in nodes]
    lons = [n.lon for n in nodes]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    def norm_lat(v): return (v - lat_min) / (lat_max - lat_min + 1e-9)
    def norm_lon(v): return (v - lon_min) / (lon_max - lon_min + 1e-9)

    coords  = torch.tensor([[norm_lat(n.lat), norm_lon(n.lon)] for n in nodes],
                           dtype=torch.float32).unsqueeze(0)
    demands = torch.tensor([n.pallets for n in nodes],
                           dtype=torch.float32).unsqueeze(0)
    cap = max(v.pallets_capacity for v in vehicles) if vehicles else 20

    with torch.no_grad():
        order = model(coords, demands, cap)[0].tolist()

    from .vrp_service import RouteTask, _route_km
    # Разбиваем order на маршруты по вместимости
    routes = []
    cur_route = []
    cur_load = 0
    for idx in order:
        n = nodes[idx]
        if cur_load + n.pallets > cap:
            if cur_route:
                routes.append(cur_route)
            cur_route = [n]
            cur_load = n.pallets
        else:
            cur_route.append(n)
            cur_load += n.pallets
    if cur_route:
        routes.append(cur_route)

    result = []
    for i, r_nodes in enumerate(routes):
        km = _route_km(r_nodes, depot_lat, depot_lon)
        hours = km / 40.0 + sum(n.service_min for n in r_nodes) / 60.0
        veh = vehicles[i % len(vehicles)] if vehicles else None
        result.append(RouteTask(vehicle=veh, nodes=r_nodes,
                                total_km=km, estimated_hours=hours))
    return result
```

### 8.2 Скрипт переобучения

```python
# api/wms_api_server/app/workers/attention_train_worker.py

import torch
import torch.optim as optim
from ..ml.attention_vrp import AttentionVRP, MODEL_PATH

def generate_synthetic(n_instances=100_000, n_nodes=50, capacity=20):
    coords  = torch.rand(n_instances, n_nodes, 2)
    demands = torch.randint(1, 9, (n_instances, n_nodes)).float()
    return coords, demands, capacity


def reinforce_loss(model, coords, demands, capacity):
    """REINFORCE с greedy baseline."""
    B = coords.size(0)
    order = model(coords, demands, capacity)
    # Reward: отрицательная сумма расстояний (упрощённо)
    pts = torch.cat([
        torch.zeros(B, 1, 2),  # depot
        coords
    ], dim=1)
    seq_idx = order + 1  # +1 для depot offset
    route_pts = torch.gather(
        pts, 1,
        seq_idx.unsqueeze(-1).expand(-1, -1, 2)
    )
    diffs = route_pts.diff(dim=1)
    lengths = diffs.norm(dim=-1).sum(dim=-1)

    baseline = lengths.mean()
    loss = ((lengths - baseline) * lengths).mean()
    return loss


def run_training(epochs=100, batch_size=256):
    model = AttentionVRP()
    opt   = optim.Adam(model.parameters(), lr=1e-4)
    coords, demands, cap = generate_synthetic()

    for epoch in range(epochs):
        idx    = torch.randperm(len(coords))[:batch_size]
        b_c, b_d = coords[idx], demands[idx]
        opt.zero_grad()
        loss = reinforce_loss(model, b_c, b_d, cap)
        loss.backward()
        opt.step()
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: loss={loss.item():.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    run_training()
```

---

## 9. Фаза 7: React — панель авто-плана

### 9.1 AutoPlanPanel.tsx

```tsx
// src/components/Transport/planning/AutoPlanPanel.tsx
import React, { useState } from 'react'
import { Button, Table, Tag, Spin, Card, Statistic, Row, Col, message } from 'antd'
import { ThunderboltOutlined, CheckOutlined } from '@ant-design/icons'
import { apiPost } from '../../../api/client'

interface PlanVariant {
  solver: 'template' | 'ortools' | 'attention' | 'clarke_wright'
  total_km: number
  estimated_hours: number
  similarity?: number
  handles_time_windows: boolean
  routes: { nodes: string[]; total_km: number; vehicle?: string }[]
}

interface Props { date: Date; onAccept: (sessionId: number, varIdx: number) => void }

const SOLVER_LABEL: Record<string, string> = {
  template:      'Шаблон',
  ortools:       'OR-Tools',
  attention:     'Нейросеть',
  clarke_wright: 'Clarke-Wright',
}

export default function AutoPlanPanel({ date, onAccept }: Props) {
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [variants, setVariants] = useState<PlanVariant[]>([])
  const [uncovered, setUncovered] = useState(0)

  const run = async () => {
    setLoading(true)
    try {
      const res = await apiPost(
        `/transport/planning/auto-plan?date=${date.toISOString().slice(0,10)}&ortools_time_limit_sec=10`,
        {}
      )
      setSessionId(res.session_id)
      setVariants(res.variants)
      setUncovered(res.uncovered_count)
    } catch {
      message.error('Ошибка авто-планирования')
    } finally {
      setLoading(false)
    }
  }

  const accept = async (idx: number) => {
    if (!sessionId) return
    await apiPost(`/transport/planning/accept?session_id=${sessionId}&variant_idx=${idx}&user_id=DISPATCHER`, {})
    onAccept(sessionId, idx)
    message.success('Рейсы созданы в системе')
  }

  return (
    <div>
      <Button
        type="primary" icon={<ThunderboltOutlined />}
        loading={loading} onClick={run}
        style={{ marginBottom: 16 }}
      >
        Сформировать авто-план
      </Button>

      {uncovered > 0 && (
        <Tag color="red" style={{ marginBottom: 8 }}>
          {uncovered} СТ без координат — не попадут в авто-план
        </Tag>
      )}

      {variants.map((v, idx) => (
        <Card
          key={idx}
          size="small"
          title={
            <span>
              <Tag color={idx === 0 ? 'gold' : 'blue'}>
                {SOLVER_LABEL[v.solver] ?? v.solver}
              </Tag>
              {v.similarity && ` · сходство ${(v.similarity * 100).toFixed(0)}%`}
              {idx === 0 && <Tag color="green" style={{ marginLeft: 8 }}>⭐ Рекомендуется</Tag>}
            </span>
          }
          extra={
            <Button
              type="primary" size="small" icon={<CheckOutlined />}
              onClick={() => accept(idx)}
            >
              Принять
            </Button>
          }
          style={{ marginBottom: 12 }}
        >
          <Row gutter={16}>
            <Col><Statistic title="Рейсов" value={v.routes.length} /></Col>
            <Col><Statistic title="Км (итого)" value={v.total_km.toFixed(1)} /></Col>
            <Col><Statistic title="Время (макс)" value={`~${v.estimated_hours.toFixed(1)} ч`} /></Col>
            <Col>
              <div>Временны́е окна</div>
              <Tag color={v.handles_time_windows ? 'green' : 'default'}>
                {v.handles_time_windows ? '✓ учтены' : '—'}
              </Tag>
            </Col>
          </Row>

          <Table
            size="small"
            style={{ marginTop: 8 }}
            dataSource={v.routes.map((r, i) => ({ key: i, ...r }))}
            pagination={false}
            columns={[
              { title: 'Рейс', render: (_,__,i) => i+1, width: 50 },
              { title: 'ТС', dataIndex: 'vehicle', width: 100 },
              { title: 'Адресов', render: (_,r) => r.nodes.length, width: 80 },
              { title: 'Км', dataIndex: 'total_km', render: v => v.toFixed(1), width: 70 },
            ]}
          />
        </Card>
      ))}
    </div>
  )
}
```

---

## 10. Фаза 8: Тесты

### 10.1 Smoke-тест (bash)

```bash
#!/bin/bash
# tests/transport/smoke.sh
BASE="http://localhost:8000"
DATE="$(date +%Y-%m-%d)"
USER="TEST_DISPATCHER"

echo "=== Smoke test: transport module ==="

# 1. Создать рейс
echo "1. Create task..."
TASK=$(curl -s -X POST "$BASE/transport/tasks?user_id=$USER" \
  -H "Content-Type: application/json" \
  -d "{\"transtype\":\"15\",\"shipment_date\":\"$DATE\",\"st_numbers\":[]}")
TASK_ID=$(echo $TASK | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")
echo "   task_id=$TASK_ID"

# 2. Получить доступные СТ
echo "2. Get available STs..."
STS=$(curl -s "$BASE/transport/pallets/available?date=$DATE&unassigned_only=true")
ST1=$(echo $STS | python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['st_number']) if d else print('')")
echo "   first ST=$ST1"

# 3. Назначить СТ на рейс
if [ -n "$ST1" ]; then
  echo "3. Assign ST $ST1 to task $TASK_ID..."
  ASSIGN=$(curl -s -X POST "$BASE/transport/tasks/$TASK_ID/assign?user_id=$USER" \
    -H "Content-Type: application/json" \
    -d "{\"st_numbers\":[\"$ST1\"]}")
  echo "   result=$(echo $ASSIGN | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("ok","ERR"))')"
fi

# 4. Оптимизировать последовательность
echo "4. Optimize sequence..."
OPT=$(curl -s -X POST "$BASE/transport/tasks/$TASK_ID/optimize-sequence?warehouse_lat=55.75&warehouse_lon=37.61")
echo "   proposed=$(echo $OPT | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d.get("proposed_order",[])))') stops"

# 5. Манифест
echo "5. Get manifest..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/transport/tasks/$TASK_ID/manifest")
echo "   HTTP $STATUS"

# 6. Снять СТ
if [ -n "$ST1" ]; then
  echo "6. Unassign ST..."
  DEL=$(curl -s -X DELETE "$BASE/transport/tasks/$TASK_ID/st/$ST1?user_id=$USER")
  echo "   result=$(echo $DEL | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("ok","ERR"))')"
fi

# 7. Отменить рейс
echo "7. Cancel task..."
CANCEL=$(curl -s -X POST "$BASE/transport/tasks/$TASK_ID/cancel?user_id=$USER")
echo "   result=$(echo $CANCEL | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("ok","ERR"))')"

echo "=== Smoke test complete ==="
```

### 10.2 Load-тест авто-плана (Python)

```python
# tests/transport/load_test_autoplan.py
import time, json, statistics, httpx

BASE    = "http://localhost:8000"
DATE    = "2026-05-21"
REPEATS = 5

results = []
for i in range(REPEATS):
    t0 = time.perf_counter()
    r  = httpx.post(
        f"{BASE}/transport/planning/auto-plan",
        params={"date": DATE, "ortools_time_limit_sec": 10},
        timeout=30
    )
    elapsed = time.perf_counter() - t0
    data = r.json()
    results.append({
        "elapsed_sec": round(elapsed, 2),
        "variants": len(data.get("variants", [])),
        "uncovered": data.get("uncovered_count", 0),
    })
    print(f"Run {i+1}: {elapsed:.2f}s, {results[-1]['variants']} variants")

report = {
    "test": "auto_plan_load",
    "date": DATE,
    "repeats": REPEATS,
    "p50_sec": round(statistics.median([r["elapsed_sec"] for r in results]), 2),
    "p95_sec": round(sorted([r["elapsed_sec"] for r in results])[int(REPEATS*0.95)-1], 2),
    "max_sec": round(max(r["elapsed_sec"] for r in results), 2),
    "target_sec": 15,
    "pass": max(r["elapsed_sec"] for r in results) <= 15,
    "runs": results,
}

with open("report.json", "w") as f:
    json.dump(report, f, indent=2)

with open("report.md", "w") as f:
    f.write(f"# Load Test: Auto Plan\n\n")
    f.write(f"**Date:** {DATE}  **Repeats:** {REPEATS}  **Target:** ≤15 sec\n\n")
    f.write(f"| Метрика | Значение |\n|---------|----------|\n")
    f.write(f"| P50 | {report['p50_sec']} сек |\n")
    f.write(f"| P95 | {report['p95_sec']} сек |\n")
    f.write(f"| Max | {report['max_sec']} сек |\n")
    f.write(f"| **Результат** | {'✅ PASS' if report['pass'] else '❌ FAIL'} |\n")

print(f"\nReport: {'PASS' if report['pass'] else 'FAIL'}")
print(f"P50={report['p50_sec']}s P95={report['p95_sec']}s Max={report['max_sec']}s")
```

---

## Сводная таблица зависимостей между фазами

```
Фаза 0 (Oracle DDL)
  └─► Фаза 1 (FastAPI базовые) — требует пакет и view
       └─► Фаза 2 (React ручной) — требует /tasks, /assign, /available
            └─► Фаза 3 (React карта) — требует координаты из available
                 ├─► Фаза 4 (OSRM) — параллельно с фазой 3
                 │    └─► Фаза 5 (OR-Tools + шаблоны) — требует матрицу
                 │         └─► Фаза 6 (Attention Model) — требует данные фазы 5
                 │              └─► Фаза 7 (React авто-план) — требует /auto-plan
                 └─► Фаза 8 (тесты) — после каждой фазы
```

---

## Итоговая оценка трудоёмкости

| Фаза | Содержание | Дней |
|------|-----------|------|
| 0 | Oracle: миграции 044–045, пакет RRL_TRANSPORT_API | 3 |
| 1 | FastAPI: все базовые эндпоинты + сервис | 3 |
| 2 | React: ручной режим (полный рабочий стол) | 5 |
| 3 | React: карта + метрики + TSP-кнопка + Gantt | 5 |
| 4 | OSRM Docker + vrp_matrix_worker | 2 |
| 5 | OR-Tools + Clarke-Wright + шаблонный движок | 4 |
| 6 | Attention Model + воркеры | 5 |
| 7 | React: панель авто-плана | 3 |
| 8 | Smoke + load тесты + evidence артефакты | 2 |
| **Итого** | | **~32 рабочих дня** |

**Минимальная рабочая версия (фазы 0–3):** ~16 дней.

---

> *Файл создан AI-ассистентом. Не редактировать вручную.*
> *Обновлено: 2026-05-21*
