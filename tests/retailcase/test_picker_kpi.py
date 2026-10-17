from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.resources.domain.picker_kpi import PickFact, summarize_picks, hourly


def fact(op, actor, previous, cumulative, boxes, line=1):
    return PickFact(op, actor, datetime(2026, 10, 16, 12, int(cumulative), tzinfo=timezone.utc),
        1, line, "SKU", "EA", Decimal(previous), Decimal(cumulative), Decimal(25),
        None if boxes is None else Decimal(boxes), None)


def test_partial_pick_credit_and_replay():
    first = fact("A", "first", 0, 24, 1)
    last = fact("B", "last", 24, 25, 0)
    result = summarize_picks([last, first, first])
    assert result["first"]["completed_lines"] == 0
    assert result["last"]["completed_lines"] == 1
    assert result["first"]["boxes"] == "1"
    assert result["last"]["quantities"][0]["quantity"] == "1"


def test_missing_proof_does_not_become_zero_boxes():
    result = summarize_picks([fact("A", "picker", 0, 25, None)])
    assert result["picker"]["boxes"] is None
    assert result["picker"]["completed_lines"] == 1


def test_fractional_box_counts_whole_boxes_and_pieces_separately():
    result=summarize_picks([fact("A","picker",0,25,"0.5")])
    assert result["picker"]["boxes"] == "0"
    assert result["picker"]["pieces"] == "25"
    assert result["picker"]["box_reasons"] == []


def test_conflicting_duplicate_is_rejected():
    with pytest.raises(ValueError):
        summarize_picks([fact("A", "one", 0, 25, 1), fact("A", "two", 0, 25, 1)])


def test_inconsistent_delta_is_rejected():
    with pytest.raises(ValueError):
        summarize_picks([fact("A", "one", 25, 24, 1)])


def test_rates_keep_two_independent_denominators():
    assert hourly(10, "2") == "5.000"
    assert hourly(10, "4") == "2.500"
    assert hourly(10, "0") is None
    assert hourly(None, "2") is None
    assert hourly(10, None) is None
