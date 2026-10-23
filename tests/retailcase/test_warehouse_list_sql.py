"""C-0169: the warehouse directory SQL selects the filtered/ordered/limited set first and aggregates cells/remains only for it (no
correlated subquery per row), keeping the
same columns, filters, order and limit. Row equality against the previous SQL on live data: reports/tradecase/2026-10-23/claude/C0169/after.json."""
import json
import pathlib
from app.services.warehouse_service import WarehouseService


class Gateway:
    def __init__(self):
        self.calls = []

    def fetch_all(self, sql, params):
        self.calls.append((" ".join(sql.split()), params)); return []


def service(gw):
    s = WarehouseService.__new__(WarehouseService); s.gateway = gw; return s


def test_counts_are_joined_aggregates_not_per_row_subqueries():
    gw = Gateway(); service(gw).list_warehouses(limit=500)
    sql, params = gw.calls[0]
    assert "(select count(*) from RRL_CELLS c where c.WARE_ID = w.ID)" not in sql and "where c.WARE_ID = w.ID" not in sql
    assert "cc as (select c.WARE_ID, count(*) CELL_COUNT from RRL_CELLS c where c.WARE_ID in (select ID from sel) group by c.WARE_ID)" in sql
    assert sql.count("where c.WARE_ID in (select ID from sel)") == 2  # aggregates bounded to the selected set
    assert "left join cc on cc.WARE_ID = sel.ID left join st on st.WARE_ID = sel.ID" in sql
    for column in ("nvl(cc.CELL_COUNT, 0) CELL_COUNT", "nvl(st.PALLET_COUNT, 0) PALLET_COUNT", "nvl(st.TOTAL_REMAIN, 0) TOTAL_REMAIN"):
        assert column in sql
    assert sql.index("order by nvl(ORD2, ID), ID") < sql.index("where rownum <= :limit") < sql.index("order by nvl(sel.ORD2, sel.ID), sel.ID")
    assert params == {"limit": 500}


def test_filters_and_limit_bounds_unchanged():
    gw = Gateway(); s = service(gw)
    s.list_warehouses(role="FINISHED_GOODS", mes_enabled=1, limit=9999); s.list_warehouses(limit=0)
    (sql, params), (_, small) = gw.calls
    assert "where nvl(FLAG_FINISHED_GOODS, 0) = 1 and nvl(MES_ENABLED, 0) = :mes_enabled" in sql
    assert params == {"limit": 500, "mes_enabled": 1} and small == {"limit": 1}


def test_live_equality_and_timing_evidence():
    report = pathlib.Path(__file__).resolve().parents[2] / "reports/tradecase/2026-10-23/claude/C0169/after.json"
    after = json.loads(report.read_text(encoding="utf-8"))
    assert after["all_equal"] and set(after["cases"]) == {"all_500", "default_200", "limit_5", "role_finished", "mes_1", "mes_0"}
