from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from app.modules.resources.domain.picker_kpi import PickFact, summarize_picks
from app.modules.resources.domain.picker_kpi_quality import ShortCompletion, ReturnedLine, append_quality

NOW = datetime(2026, 10, 17, 5, tzinfo=timezone.utc)


def pick(op="P1", actor="picker", previous="0", cumulative="24", boxes="1", at=NOW):
    return PickFact(op, actor, at, 1, 10, "SKU", "EA", D(previous), D(cumulative), D(25), D(boxes), None, D(24), "BOX_SCAN")


def test_approved_short_credits_physical_finisher_once_not_manager():
    facts = [pick(actor="first", cumulative="12", boxes="0"),
        pick("P2", "last", "12", "24", "0", NOW + timedelta(seconds=1))]
    facts = [replace(fact, box_size_base=None, input_kind="BASE_SCAN") for fact in facts]
    closure = ShortCompletion("APPROVAL_BY_MANAGER", NOW + timedelta(minutes=2), 1, 10, D(24), D(25), D(1))
    totals = summarize_picks(facts); append_quality(totals, facts, [closure, closure], [])
    assert totals["first"]["completed_lines"] == 0
    assert totals["last"]["completed_lines"] == 1
    assert totals["last"]["shortage_completed_lines"] == 1
    assert "manager" not in totals
    assert totals["last"]["line_completions"][0]["at"] == facts[-1].at.isoformat()


def test_return_preserves_work_and_reports_quantity_without_unit_conversion():
    facts = [pick()]; returned = ReturnedLine("RETURN", NOW + timedelta(minutes=3), 1, 10, "SKU", "EA", D(24))
    totals = summarize_picks(facts); append_quality(totals, facts, [], [returned, returned])
    assert totals["picker"]["boxes"] == "1" and totals["picker"]["pieces"] == "0"
    assert totals["picker"]["return_events"] == 1
    assert totals["picker"]["returned_quantities"] == [{"article": "SKU", "base_uom": "EA", "quantity": "24"}]


def test_frozen_partial_box_policy_and_unboxed_piece():
    item = replace(pick(cumulative="25", boxes="0"), boxes=None, packaging_reason="PARTIAL_BOX_RULE_REQUIRED")
    totals = summarize_picks([item]); assert totals["picker"]["boxes"] == "1" and totals["picker"]["pieces"] == "1"
    piece = replace(pick(cumulative="1", boxes="0"), box_size_base=None, input_kind="BASE_SCAN")
    totals = summarize_picks([piece]); assert totals["picker"]["boxes"] == "0" and totals["picker"]["pieces"] == "1"


def test_full_line_does_not_double_count_a_shortage_decision():
    facts = [replace(pick(cumulative="25", boxes="0"), box_size_base=None)]
    totals = summarize_picks(facts); append_quality(totals, facts, [], [])
    assert totals["picker"]["completed_lines"] == 1 and totals["picker"]["shortage_completed_lines"] == 0
    assert totals["picker"]["line_completions"][0]["kind"] == "FULL"


def test_other_line_returns_do_not_leak_into_own_quality():
    facts = [pick()]; totals = summarize_picks(facts)
    append_quality(totals, facts, [], [ReturnedLine("FOREIGN", NOW, 1, 99, "PRIVATE", "KG", D(10))])
    assert totals["picker"]["return_events"] == 0 and totals["picker"]["returned_quantities"] == []
