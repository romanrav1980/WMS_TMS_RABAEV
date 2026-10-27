"""C-0174: after the wave adopted a top-up's holds, a part of the SAP order left out of a reduced TRIP is not counted again as extra
load of that trip; before adoption a confirmed top-up still occupies its full space. Recorded live readings of the own 6+3 -> 8/1 run."""
import json
import pathlib
from decimal import Decimal
from app.modules.integrations.infrastructure import trade_topup

ROOT = pathlib.Path(__file__).resolve().parents[2]
ORDERS = {"MAIN": {"lines": [{"line_id": "1", "uom": "EA"}]}, "O104": {"lines": [{"line_id": "1", "uom": "EA"}]}}
RUN = json.loads((ROOT / "tests/fixtures/tradecase_topup_reduction_20261027.json").read_text(encoding="utf-8"))


class Cur:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, sql, **kw):
        assert "RRL_TRADE_TOPUP_HOLD" in sql and "STATUS='ACTIVE'" in sql and "SAP_ACCEPTED" in sql

    def fetchall(self):
        return self.rows


def confirmed(monkeypatch, row, trip_quantity):
    monkeypatch.setattr(trade_topup, "_document", lambda cur, ware, kind, key: (ORDERS[key], 1))
    trip = {"orders": [{"order_id": "MAIN", "line_id": "1", "quantity": 60}] + ([{"order_id": "O104", "line_id": "1", "quantity": trip_quantity}] if trip_quantity else [])}
    got = trade_topup._confirmed(Cur([row]), 1, "T1", trip)[0]
    return got["inside"], got["extra"]


def test_before_adoption_confirmed_topup_occupies_its_space(monkeypatch):
    assert confirmed(monkeypatch, ("N1", "A", 3, "O104", 10, 30), 0) == (Decimal(0), Decimal(3))
    assert confirmed(monkeypatch, ("N1", "A", 3, None, 10, 30), 0) == (Decimal(0), Decimal(3))


def test_adopted_topup_left_out_of_a_reduced_trip_is_not_phantom_load(monkeypatch):
    assert confirmed(monkeypatch, ("N1", "A", 3, "O104", 10, 0), 20) == (Decimal(2), Decimal(0))  # 3 approved, 2 on the trip, holds ADOPTED


def test_partial_adoption_counts_only_still_active_holds(monkeypatch):
    assert confirmed(monkeypatch, ("N1", "A", 40, "O104", 10, 100), 150) == (Decimal(15), Decimal(10))  # 25 not in TRIP, only 10 still held


def test_recorded_live_readings():
    before, after = RUN["capacity"]["before_reduction"], RUN["capacity"]["after_reduction"]
    assert before["plain_planned_m3"] == before["topup_planned_m3"] == "0.9" and before["holds"] == [["ADOPTED", 3, 30]]
    assert after["plain_planned_m3"] == "0.8" and after["topup_planned_m3"] == "0.9"  # the confirmed live phantom box (old code)
    assert RUN["fixed_in_process"]["planned_volume_m3"] == "0.8" and RUN["fixed_in_process"]["sender_stock_boxes"] is None
