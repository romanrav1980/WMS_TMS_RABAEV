import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import json
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.schemas import MesRawIssueRequest,MesCompleteOrderRequest,MesCompletionPallet
from app.services.mes_service import MesService
from fastapi import HTTPException


def test_mes_qty_keeps_large_decimal_in_oracle_bind_and_pallet_json():
    q="9007199254740993.000000001"
    raw=MesRawIssueRequest(quantity=q)
    complete=MesCompleteOrderRequest(fact_qty=q,pallets=[MesCompletionPallet(uid_pallet="legacy",quantity=q)])
    assert raw.quantity==Decimal(q) and complete.fact_qty==Decimal(q)
    payload=json.loads(json.dumps([p.model_dump(mode="json") for p in complete.pallets]))
    assert payload[0]["quantity"]==q


@pytest.mark.parametrize("qty",["NaN","Infinity","-1","0","0.0000000001"])
def test_invalid_physical_quantity_rejected_before_oracle(qty):
    with pytest.raises(ValidationError):
        MesRawIssueRequest(quantity=qty)
    with pytest.raises(ValidationError):
        MesCompleteOrderRequest(fact_qty=qty)


def test_private_reservation_cannot_write_after_activation():
    class Gateway:
        def fetch_all(self,*args):return [{"state":"ACTIVE"}]
        def execute(self,*args):raise AssertionError("Unexpected legacy reservation DML")
        def call_number_plsql(self,*args):raise AssertionError("Unexpected sequence before admission")
    with pytest.raises(HTTPException) as error:
        MesService(Gateway())._create_hard_raw_reservation(1,{}, "operator")
    assert error.value.detail["code"]=="MES_RESERVATION_POSTING_REQUIRED"
