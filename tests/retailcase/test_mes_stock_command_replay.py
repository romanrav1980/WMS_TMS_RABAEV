"""Regression: an MES retry uses its committed envelope, not the current pending set."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
import pytest
from fastapi import HTTPException
from app.schemas import MesApplyWmsRequest, MesReleaseToProductionRequest
from app.modules.inventory.infrastructure import mes_commands, mes_release_commands
from app.services.mes_service import MesService


class ReplayGateway:
    def __init__(self, original, authorized=True):
        self.original = original
        self.authorized = authorized
        self.calls = []
    def fetch_all(self, sql, params=None):
        self.calls.append(sql)
        if "RRL_STOCK_RELEASE" in sql:
            return [{"state": "ACTIVE"}]
        if "RRL_PRODUCTION_ORDER" in sql and "ALLOWED" in sql:
            return [{"allowed": 1}] if self.authorized else []
        if "CANONICAL_REQUEST" in sql:
            return [{"canonical_request": json.dumps(self.original)}]
        raise AssertionError("Replay must not resolve current MES movements or document status")


def envelope():
    return {"command_type": "MES_MOVEMENTS", "actor": "operator",
            "source": {"type": "PRODUCTION_ORDER", "production_order_id": 7,
                       "movement_ids": [11, 12]},
            "metadata": {"units_by_movement": {}}}


def test_implicit_retry_restores_original_movements(monkeypatch):
    captured = []
    def post(command):
        captured.append(command)
        return {"operation_id": command.operation_id, "applied": 2}
    monkeypatch.setattr(mes_commands, "_post", post)
    result = mes_commands.apply_mes_movements(
        ReplayGateway(envelope()), 7, MesApplyWmsRequest(operation_id="saved"), "operator")
    assert result["applied"] == 2
    assert captured[0].source["movement_ids"] == [11, 12]


def test_retry_rechecks_current_access_before_reading_the_saved_envelope(monkeypatch):
    gateway = ReplayGateway(envelope(), authorized=False)
    monkeypatch.setattr(mes_commands, "_post", lambda _: pytest.fail("Revoked actor posted"))
    with pytest.raises(HTTPException) as error:
        mes_commands.apply_mes_movements(gateway, 7, MesApplyWmsRequest(operation_id="saved"), "operator")
    assert error.value.status_code == 403
    assert error.value.detail["code"] == "MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED"
    assert not any("CANONICAL_REQUEST" in sql for sql in gateway.calls)


@pytest.mark.parametrize("change", ["actor", "order", "units", "ids"])
def test_same_id_changed_request_rejected_before_posting(monkeypatch, change):
    monkeypatch.setattr(mes_commands, "_post", lambda _: pytest.fail("Conflicting replay posted"))
    request = MesApplyWmsRequest(operation_id="saved",
        movement_ids=[11] if change == "ids" else None,
        units_by_movement={"11": ["different"]} if change == "units" else {})
    with pytest.raises(HTTPException) as error:
        mes_commands.apply_mes_movements(ReplayGateway(envelope()),
            8 if change == "order" else 7, request,
            "other" if change == "actor" else "operator")
    assert error.value.status_code == 409
    assert error.value.detail["code"] == "OPERATION_CONFLICT"


def test_release_retry_enters_core_before_closed_order_check(monkeypatch):
    class Posting:
        def post(self, command):
            assert command.operation_id == "release-saved"
            assert command.source == {"production_order_id": 7}
            return {"operation_id": command.operation_id, "task_count": 2, "shortage_count": 0}
    monkeypatch.setattr(mes_release_commands, "StockPosting", Posting)
    result = MesService(ReplayGateway(envelope())).release_to_production(
        7, MesReleaseToProductionRequest(operation_id="release-saved", created_by="operator"))
    assert result["created_task_count"] == 2
