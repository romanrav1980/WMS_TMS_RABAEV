from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_acceptance_runbook_exists():
    source = (ROOT / "wiki/runbooks/tms2_release_acceptance.md").read_text(encoding="utf-8")
    for token in (
        "TMS-2 Release Acceptance Runbook",
        "055_apply.sql",
        "tms2-release-gate.ps1",
        "TMS_RUN_MUTATING_VRP_APPLY",
        "transport_table_2000_nfr_smoke.cjs",
    ):
        assert token in source


def test_pilot_checklist_exists():
    source = (ROOT / "wiki/runbooks/tms2_pilot_checklist.md").read_text(encoding="utf-8")
    for token in (
        "TMS-2 Pilot Checklist",
        "5 consecutive working days",
        "C# WinForms",
        "Incident Log",
        "Stop Criteria",
    ):
        assert token in source
