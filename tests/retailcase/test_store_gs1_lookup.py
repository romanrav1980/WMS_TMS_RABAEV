"""GS1 fallback must preserve legacy exact matches, scope and original scan ACK."""
from contextlib import contextmanager
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
import pytest
from fastapi import HTTPException
from app.modules.delivery.infrastructure import store_app_reads as owner
from app.modules.delivery.contracts import StoreReceiptError

SSCC='090000000000010017'


class Cursor:
    def __init__(self,answers):self.answers=iter(answers);self.scans=[];self.statements=[]
    def execute(self,sql,**params):
        self.statements.append(sql)
        if 'scan'in params:self.scans.append(params['scan']);assert params['address']=='QA_ADDR'
    def fetchall(self):return next(self.answers)


class Gateway:
    def __init__(self,answers):self.cursor=Cursor(answers)
    @contextmanager
    def transaction(self,_):yield self.cursor


@pytest.fixture(autouse=True)
def current_scope(monkeypatch):
    monkeypatch.setattr(owner,'selected_store',lambda cur,actor,store:{'store_addr':'QA_ADDR'})


@pytest.mark.parametrize('code',['00'+SSCC,'(00)'+SSCC,']C100'+SSCC,']C1(00)'+SSCC])
def test_gs1_fallback_keeps_original_echo_and_bounded_query(code):
    g=Gateway([[],[('LOAD',None)]])
    result=owner.StoreAppReads(g).lookup('receiver','QA',code)
    assert result==dict(load_operation_id='LOAD',store_id='QA',scanned_code=code)
    assert g.cursor.scans==[code,SSCC]
    assert all('fetch first 2 rows only'in sql for sql in g.cursor.statements[1:])


def test_exact_twenty_digit_internal_id_wins_over_sscc_alias():
    code='00'+SSCC;g=Gateway([[('INTERNAL20',None)]])
    assert owner.StoreAppReads(g).lookup('receiver','QA',code)['load_operation_id']=='INTERNAL20'
    assert g.cursor.scans==[code]


def test_ambiguous_exact_match_does_not_fall_back_to_different_place():
    g=Gateway([[('LOAD_A',None),('LOAD_B',None)]])
    with pytest.raises(StoreReceiptError)as error:owner.StoreAppReads(g).lookup('receiver','QA','00'+SSCC)
    assert error.value.code=='STORE_SCAN_AMBIGUOUS'and len(g.cursor.scans)==1


@pytest.mark.parametrize('code,scans',[(SSCC,[SSCC]),('PALLET-1',['PALLET-1']),('00'+SSCC,['00'+SSCC,SSCC])])
def test_missing_stays_missing_without_unbounded_alias_search(code,scans):
    g=Gateway([[]for _ in scans])
    with pytest.raises(StoreReceiptError)as error:owner.StoreAppReads(g).lookup('receiver','QA',code)
    assert error.value.code=='STORE_SCAN_NOT_FOUND'and g.cursor.scans==scans


def test_scope_denial_precedes_both_exact_and_alias_lookup(monkeypatch):
    def denied(*args):raise HTTPException(403,'revoked')
    monkeypatch.setattr(owner,'selected_store',denied);g=Gateway([])
    with pytest.raises(HTTPException):owner.StoreAppReads(g).lookup('receiver','QA','00'+SSCC)
    assert g.cursor.scans==[]and g.cursor.statements==['set transaction read only']
