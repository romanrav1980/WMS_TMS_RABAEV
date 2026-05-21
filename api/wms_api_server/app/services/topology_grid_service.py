"""
topology_grid_service.py — Сервис создания топологии из grid-редактора.

Точка входа: create_topology_from_grid().
Принимает payload в виде GridPayload (Pydantic-модель из schemas.py),
транзакционно создаёт все Oracle-объекты:

    RRL_WAREHOUSE_TOPOLOGY  (status='DRAFT')
      └── RRL_TOPOLOGY_AISLE  (по одному на каждую аллею)
           └── RRL_TOPOLOGY_CELL  (левые и правые ячейки)
                └── RRL_TOPOLOGY_PICK_FACE_SLOT  (мелкоштучные слоты, если заданы)
    RRL_PICK_ROUTE  (status='DRAFT')
      └── RRL_PICK_ROUTE_CELL  (строки с pick_sequence)

Все INSERT идут напрямую через OracleGateway.execute_many() без PL/SQL-пакета,
т.к. данные поступают пачкой из редактора, а не через оперативный UI операций.
"""

from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import GridPayload


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

# Алфавит кодов столбцов: A, B, ..., Z, AA, AB, ...
def _col_code(col: int) -> str:
    """
    Преобразовать 1-based номер столбца в буквенный код (A, B, ..., Z, AA, ...).
    Совпадает с функцией colLabel() на фронтенде.
    """
    result = ""
    n = col
    while n > 0:
        n -= 1
        result = chr(65 + (n % 26)) + result
        n //= 26
    return result


# Коды уровней для мелкоштучных слотов: А, Б, В, Г, Д
_SLOT_ROW_LABELS = ["А", "Б", "В", "Г", "Д"]


def _slot_code(slot_col: int, slot_row: int) -> str:
    """
    Сформировать код слота вида 'А1', 'Б3' и т.д.
    slot_row = 1 → нижний уровень (А), slot_row = 5 → верхний (Д).
    """
    row_label = _SLOT_ROW_LABELS[slot_row - 1] if slot_row <= 5 else str(slot_row)
    return f"{row_label}{slot_col}"


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

class TopologyGridService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def create_topology_from_grid(
        self,
        payload: GridPayload,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Транзакционно создаёт топологию из данных grid-редактора.

        Возвращает:
            {
                "topology_id": int,
                "status":      "DRAFT",
                "cell_count":  int,
                "slot_count":  int,
                "aisle_count": int,
            }
        """
        with self.gateway._open_connection() as conn:
            try:
                result = self._create(conn, payload, user_id)
                conn.commit()
                return result
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=500, detail=str(exc)) from exc

    # -----------------------------------------------------------------------
    # Внутренняя логика (всё в одном соединении)
    # -----------------------------------------------------------------------

    def _create(
        self,
        conn: Any,
        payload: GridPayload,
        user_id: str,
    ) -> dict[str, Any]:
        cursor = conn.cursor()

        # ---- 1. Создать топологию ----
        topology_id = self._nextval(cursor, "RRL_WAREHOUSE_TOPOLOGY_SEQ")
        cursor.execute(
            """
            INSERT INTO RABAEV.RRL_WAREHOUSE_TOPOLOGY
              (TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME,
               STATUS, VERSION_NO, CREATED_BY, CREATED_AT)
            VALUES
              (:1, :2, :3, :4, 'DRAFT', 1, :5, SYSDATE)
            """,
            [
                topology_id,
                payload.warehouse_id,
                f"GRID-{topology_id}",
                payload.label,
                user_id,
            ],
        )

        # ---- 2. Создать аллеи ----
        # aisle_local_id → db_aisle_id для привязки ячеек
        aisle_id_map: dict[str, int] = {}

        for i, aisle in enumerate(payload.grid.aisles):
            db_aisle_id = self._nextval(cursor, "RRL_TOPOLOGY_AISLE_SEQ")
            aisle_id_map[aisle.id] = db_aisle_id

            # Расстояние по умолчанию: index × ширина_прохода
            dist = aisle.distance_meters
            if dist is None:
                dist = i * (payload.grid.settings.aisle_width_meters or 3.5)

            cursor.execute(
                """
                INSERT INTO RABAEV.RRL_TOPOLOGY_AISLE
                  (AISLE_ID, TOPOLOGY_ID, AISLE_CODE, AISLE_NAME, AISLE_LABEL,
                   AISLE_KIND, DISTANCE_FROM_START_M, AISLE_WIDTH_M,
                   ACTIVE, X1, Y1, X2, Y2, WIDTH_M)
                VALUES
                  (:1, :2, :3, :4, :5,
                   'PICK', :6, :7,
                   1, 0, 0, 0, :8, :9)
                """,
                [
                    db_aisle_id,
                    topology_id,
                    aisle.id,                            # AISLE_CODE
                    aisle.label,                         # AISLE_NAME
                    aisle.label,                         # AISLE_LABEL
                    dist,                                # DISTANCE_FROM_START_M
                    payload.grid.settings.aisle_width_meters or 3.5,
                    payload.grid.rows,                   # X2/Y2 (приблизительно)
                    payload.grid.settings.aisle_width_meters or 3.5,
                ],
            )

        # ---- 3. Создать ячейки ----
        # cell_lookup: (row, col) → cell_id — для маршрута
        cell_lookup: dict[tuple[int, int], int] = {}
        slot_count = 0

        for cell in payload.grid.cells:
            if cell.role not in ("left", "right"):
                continue

            cell_id = self._nextval(cursor, "RRL_TOPOLOGY_CELL_SEQ")
            cell_lookup[(cell.row, cell.col)] = cell_id

            db_aisle_id = (
                aisle_id_map.get(cell.aisle_id)
                if cell.aisle_id
                else None
            )
            side_code = "LEFT" if cell.role == "left" else "RIGHT"
            section   = _col_code(cell.col)

            cursor.execute(
                """
                INSERT INTO RABAEV.RRL_TOPOLOGY_CELL
                  (CELL_ID, TOPOLOGY_ID, AISLE_ID, AISLE_CODE,
                   BAY_NO, SECTION_CODE, SIDE_CODE,
                   CELL_CODE, CELL_KIND, IS_PICK_FACE,
                   ACTIVE, X, Y, Z, WIDTH, DEPTH, HEIGHT)
                VALUES
                  (:1, :2, :3, :4,
                   :5, :6, :7,
                   :8, 'PICK_FACE', 1,
                   1, :9, :10, 0, 1.1, 1.1, 1.4)
                """,
                [
                    cell_id,
                    topology_id,
                    db_aisle_id,
                    # AISLE_CODE — ищем по db_aisle_id
                    next(
                        (a.id for a in payload.grid.aisles if aisle_id_map.get(a.id) == db_aisle_id),
                        None,
                    ),
                    cell.row,            # BAY_NO
                    section,             # SECTION_CODE
                    side_code,           # SIDE_CODE
                    f"{section}{cell.row:03d}{side_code[0]}",  # CELL_CODE
                    # Приблизительные координаты для SVG-вьювера
                    cell.col * 1.1,      # X
                    cell.row * 1.4,      # Y
                ],
            )

            # ---- 3a. Мелкоштучные слоты ----
            if cell.slot_division and (
                cell.slot_division.cols > 1 or cell.slot_division.rows > 1
            ):
                sc = max(1, cell.slot_division.cols)
                sr = max(1, cell.slot_division.rows)

                for slot_row in range(1, sr + 1):
                    for slot_col in range(1, sc + 1):
                        slot_id = self._nextval(
                            cursor, "RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ"
                        )
                        cursor.execute(
                            """
                            INSERT INTO RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT
                              (SLOT_ID, CELL_ID, SLOT_COL, SLOT_ROW, SLOT_CODE, IS_ACTIVE)
                            VALUES (:1, :2, :3, :4, :5, 1)
                            """,
                            [slot_id, cell_id, slot_col, slot_row,
                             _slot_code(slot_col, slot_row)],
                        )
                        slot_count += 1

        # ---- 4. Создать маршрут ----
        route_id = None
        if payload.grid.pick_sequences:
            route_id = self._nextval(cursor, "RRL_PICK_ROUTE_SEQ")
            cursor.execute(
                """
                INSERT INTO RABAEV.RRL_PICK_ROUTE
                  (PICK_ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_NAME,
                   ROUTE_PATTERN, STATUS)
                VALUES (:1, :2, 'MAIN', 'Основной маршрут', :3, 'DRAFT')
                """,
                [route_id, topology_id, payload.grid.route_pattern or "U"],
            )

            # Вставить ячейки маршрута пакетом
            route_rows = []
            for seq_item in payload.grid.pick_sequences:
                cell_id = cell_lookup.get((seq_item.row, seq_item.col))
                if cell_id is not None:
                    rrc_id = self._nextval(cursor, "RRL_PICK_ROUTE_CELL_SEQ")
                    route_rows.append(
                        [rrc_id, route_id, cell_id, seq_item.pick_sequence]
                    )

            if route_rows:
                cursor.executemany(
                    """
                    INSERT INTO RABAEV.RRL_PICK_ROUTE_CELL
                      (PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, TOPOLOGY_CELL_ID, PICK_SEQUENCE)
                    VALUES (:1, :2, :3, :4)
                    """,
                    route_rows,
                )

        return {
            "topology_id": topology_id,
            "status":      "DRAFT",
            "cell_count":  len(cell_lookup),
            "slot_count":  slot_count,
            "aisle_count": len(aisle_id_map),
        }

    def get_topology_as_grid(self, topology_id: int) -> dict[str, Any]:
        """
        Загружает топологию из БД и возвращает GridState-совместимый словарь
        для повторного открытия в редакторе.
        """
        with self.gateway._open_connection() as conn:
            cursor = conn.cursor()

            # -- Заголовок топологии --
            cursor.execute(
                """
                SELECT TOPOLOGY_CODE, TOPOLOGY_NAME, WARE_ID
                  FROM RABAEV.RRL_WAREHOUSE_TOPOLOGY
                 WHERE TOPOLOGY_ID = :1
                """,
                [topology_id],
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Topology not found")
            topo_code, topo_name, ware_id = row

            # -- Аллеи --
            cursor.execute(
                """
                SELECT AISLE_ID, AISLE_CODE, AISLE_LABEL,
                       DISTANCE_FROM_START_M, AISLE_WIDTH_M
                  FROM RABAEV.RRL_TOPOLOGY_AISLE
                 WHERE TOPOLOGY_ID = :1
                 ORDER BY DISTANCE_FROM_START_M NULLS LAST, AISLE_ID
                """,
                [topology_id],
            )
            aisle_rows = cursor.fetchall()

            # aisle_db_id → aisle_code (строка)
            aisle_id_to_code: dict[int, str] = {r[0]: r[1] for r in aisle_rows}

            aisles = [
                {
                    "id":               r[1],
                    "label":            r[2] or r[1],
                    "distance_meters":  float(r[3]) if r[3] is not None else None,
                    "aisle_width_meters": float(r[4]) if r[4] is not None else None,
                }
                for r in aisle_rows
            ]

            # -- Ячейки --
            cursor.execute(
                """
                SELECT c.CELL_ID, c.BAY_NO, c.SECTION_CODE, c.SIDE_CODE, c.AISLE_ID
                  FROM RABAEV.RRL_TOPOLOGY_CELL c
                 WHERE c.TOPOLOGY_ID = :1
                   AND c.CELL_KIND = 'PICK_FACE'
                """,
                [topology_id],
            )
            cell_rows = cursor.fetchall()

            # cell_id → (row, col_num) для маршрута
            def _col_num(section_code: str) -> int:
                n = 0
                for ch in section_code:
                    n = n * 26 + (ord(ch) - 64)
                return n

            cell_id_to_pos: dict[int, tuple[int, int]] = {}
            cells = []
            for cell_id, bay_no, section_code, side_code, aisle_db_id in cell_rows:
                col = _col_num(section_code) if section_code else 0
                row = int(bay_no) if bay_no else 0
                cell_id_to_pos[cell_id] = (row, col)
                cells.append({
                    "row":      row,
                    "col":      col,
                    "role":     "left" if side_code == "LEFT" else "right",
                    "aisle_id": aisle_id_to_code.get(aisle_db_id) if aisle_db_id else None,
                    "slot_division": None,
                })

            # -- Слоты --
            cursor.execute(
                """
                SELECT s.CELL_ID, MAX(s.SLOT_COL), MAX(s.SLOT_ROW)
                  FROM RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT s
                  JOIN RABAEV.RRL_TOPOLOGY_CELL c
                    ON c.CELL_ID = s.CELL_ID
                 WHERE c.TOPOLOGY_ID = :1
                 GROUP BY s.CELL_ID
                """,
                [topology_id],
            )
            slot_rows = {r[0]: {"cols": int(r[1]), "rows": int(r[2])} for r in cursor.fetchall()}

            # Вставить slot_division в cells
            cell_map_by_id: dict[int, dict] = {}
            for (cell_id, _bay, _sec, _side, _aisle), cell_obj in zip(cell_rows, cells):
                cell_map_by_id[cell_id] = cell_obj
                if cell_id in slot_rows:
                    cell_obj["slot_division"] = slot_rows[cell_id]

            # -- Маршрут --
            cursor.execute(
                """
                SELECT r.ROUTE_PATTERN
                  FROM RABAEV.RRL_PICK_ROUTE r
                 WHERE r.TOPOLOGY_ID = :1
                   AND ROWNUM = 1
                 ORDER BY r.PICK_ROUTE_ID
                """,
                [topology_id],
            )
            route_row = cursor.fetchone()
            route_pattern = route_row[0] if route_row else "U"

            cursor.execute(
                """
                SELECT rc.TOPOLOGY_CELL_ID, rc.PICK_SEQUENCE
                  FROM RABAEV.RRL_PICK_ROUTE_CELL rc
                  JOIN RABAEV.RRL_PICK_ROUTE r
                    ON r.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
                 WHERE r.TOPOLOGY_ID = :1
                 ORDER BY rc.PICK_SEQUENCE
                """,
                [topology_id],
            )
            pick_sequences = []
            for cell_id, seq in cursor.fetchall():
                pos = cell_id_to_pos.get(cell_id)
                if pos:
                    pick_sequences.append({"row": pos[0], "col": pos[1], "pick_sequence": int(seq)})

            # -- Определить размеры сетки --
            max_row = max((c["row"] for c in cells), default=10)
            max_col = max((c["col"] for c in cells), default=10)

            return {
                "topology_id":   topology_id,
                "topology_code": topo_code,
                "label":         topo_name,
                "warehouse_id":  ware_id,
                "grid": {
                    "rows":           max_row,
                    "cols":           max_col,
                    "route_pattern":  route_pattern,
                    "aisles":         aisles,
                    "cells":          cells,
                    "pick_sequences": pick_sequences,
                    "settings": {
                        "aisle_width_meters": float(aisle_rows[0][4]) if aisle_rows and aisle_rows[0][4] else 3.5,
                        "bay_height_meters":  1.4,
                    },
                },
            }

    @staticmethod
    def _nextval(cursor: Any, sequence: str) -> int:
        """Получить следующее значение Oracle-последовательности."""
        cursor.execute(f"SELECT RABAEV.{sequence}.NEXTVAL FROM DUAL")
        return cursor.fetchone()[0]
