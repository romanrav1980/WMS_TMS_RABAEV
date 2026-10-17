"""Pure boundaries: strict actor input, native context and old close replay ordering."""
from contextlib import contextmanager
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from app.modules.inventory.contracts_case_current_close import CaseCurrentCloseInput
from app.modules.inventory.contracts_case_close import CaseCarrierCloseRequest
from app.modules.inventory.infrastructure import case_carrier_close as owner
from app.modules.inventory.infrastructure import case_current_close as adapter


@pytest.mark.parametrize("changes", [{"actor":"admin"},{"operation_id":""},{"expected_content_version":True},{"expected_content_version":-1},{"task_id":9}])
def test_current_input_is_strict_identity_only(changes):
    body={"operation_id":"CLOSE:1","expected_content_version":2,**changes}
    with pytest.raises(ValidationError):CaseCurrentCloseInput.model_validate(body)


class Cursor:
    def __init__(self):self.calls=[]
    def execute(self,sql,**kwargs):self.calls.append(sql)
    def fetchone(self):return ("IN_PROGRESS",2,"picker",None)


def test_original_replay_precedes_new_eligibility_and_old_context_not_called(monkeypatch):
    cursor=Cursor();trace=[]
    @contextmanager
    def context(*args):
        trace.append("begin");yield cursor;trace.append("end")
    def scope(*args):trace.append("current")
    monkeypatch.setattr(owner,"receipt_task_metadata",lambda *a:pytest.fail("Legacy flat metadata path used"))
    monkeypatch.setattr(owner,"close_replay",lambda *a:{"saved":True})
    result=owner.close_case_carrier(object(),7,CaseCarrierCloseRequest(operation_id="CLOSE:1",expected_content_version=2,actor="picker"),scope,
        metadata_context=context,assert_new=lambda *a:pytest.fail("Historical receipt requires new execution eligibility"))
    assert result=={"saved":True} and trace==["begin","current","current","end"]
    assert not any("update "in sql.lower()for sql in cursor.calls)


def test_new_close_native_denial_precedes_content_validation_and_effects(monkeypatch):
    cursor=Cursor();trace=[]
    @contextmanager
    def context(*args):
        try:yield cursor
        finally:trace.append("end")
    monkeypatch.setattr(owner,"close_replay",lambda *a:None)
    monkeypatch.setattr(owner,"validate_close_content",lambda *a:pytest.fail("Validation ran before native new-close admission"))
    def deny(*args):raise HTTPException(403,"revoked")
    with pytest.raises(HTTPException)as error:
        owner.close_case_carrier(object(),7,CaseCarrierCloseRequest(operation_id="CLOSE:1",expected_content_version=2,actor="picker"),lambda *a:None,metadata_context=context,assert_new=deny)
    assert error.value.status_code==403 and trace==["end"]
    assert not any("update "in sql.lower()for sql in cursor.calls)


def test_adapter_bindings_keep_server_actor_and_native_context(monkeypatch):
    calls=[]
    class NativeCursor:
        def callproc(self,name,args=()):calls.append((name,list(args)))
    class Gateway:
        @contextmanager
        def transaction(self,purpose):yield NativeCursor()
    def existing(gateway,task,request,current,**options):
        assert request.actor=="picker" and task==7
        with options["metadata_context"](gateway,"close","picker","case_pick_execute")as cursor:
            current(cursor,task,"picker","case_pick_execute");options["assert_new"](cursor,task,"picker")
        return {"status":"WAIT_CONTROL","content_version":2,"already_closed":False,"physical_stock_changed":False}
    monkeypatch.setattr(adapter,"close_case_carrier",existing)
    result=adapter.CaseCurrentClose(Gateway()).close(7,CaseCurrentCloseInput(operation_id="CLOSE:1",expected_content_version=2),"picker")
    assert result["operation_id"]=="CLOSE:1"
    assert calls==[("RRL_CASE_LIFECYCLE_API.begin_close",[7,"picker"]),("RRL_CASE_LIFECYCLE_API.task_current_scope",[7,"picker"]),("RRL_CASE_LIFECYCLE_API.assert_new_close",[7,"picker"]),("RRL_CASE_LIFECYCLE_API.end_close",[])]


def test_failed_begin_does_not_end_foreign_context(monkeypatch):
    calls=[]
    class NativeCursor:
        def callproc(self,name,args=()):calls.append(name);raise HTTPException(409,"nested")
    class Gateway:
        @contextmanager
        def transaction(self,purpose):yield NativeCursor()
    def existing(gateway,task,request,current,**options):
        with options["metadata_context"](gateway,"close","picker","case_pick_execute"):pytest.fail("begin unexpectedly succeeded")
    monkeypatch.setattr(adapter,"close_case_carrier",existing)
    with pytest.raises(HTTPException):adapter.CaseCurrentClose(Gateway()).close(7,CaseCurrentCloseInput(operation_id="CLOSE:1",expected_content_version=2),"picker")
    assert calls==["RRL_CASE_LIFECYCLE_API.begin_close"]

@pytest.mark.parametrize('bad', [None, [], {'status':'WAIT_CONTROL'}, {'status':'WAIT_CONTROL','content_version':True,'already_closed':False,'physical_stock_changed':False}, {'status':'WAIT_CONTROL','content_version':2,'already_closed':False,'physical_stock_changed':True}, {'status':'WAIT_CONTROL','content_version':2,'already_closed':False,'physical_stock_changed':False,'operation_id':'FOREIGN'}])
def test_malformed_replay_ack_rolls_back_inside_owner_uow(monkeypatch,bad):
    trace=[]
    class NativeCursor(Cursor):
        def callproc(self,name,args=()):trace.append(name)
    class Gateway:
        @contextmanager
        def transaction(self,purpose):
            try:yield NativeCursor()
            except Exception:
                trace.append('rollback');raise
            else:trace.append('commit')
    # None means no receipt in the old owner; missing-result journal instead raises KeyError.
    def replay(*args):
        if bad is None:raise KeyError('result')
        return bad
    monkeypatch.setattr(owner,'close_replay',replay)
    with pytest.raises(HTTPException)as error:
        adapter.CaseCurrentClose(Gateway()).close(7,CaseCurrentCloseInput(operation_id='CLOSE:1',expected_content_version=2),'picker')
    assert error.value.status_code==503 and error.value.detail['code']=='CASE_CURRENT_CLOSE_ACK_INVALID'
    assert trace[-1]=='rollback' and 'commit'not in trace
    assert 'RRL_CASE_LIFECYCLE_API.end_close'in trace


@pytest.mark.parametrize('saved',[{'result':None},{'result':[]},{}])
def test_real_saved_null_or_missing_ack_cannot_become_new_close(monkeypatch,saved):
    import json
    trace=[]
    body=CaseCurrentCloseInput(operation_id='CLOSE:1',expected_content_version=2)
    request=CaseCarrierCloseRequest(**body.model_dump(),actor='picker').model_dump(mode='json')
    class NativeCursor(Cursor):
        def callproc(self,name,args=()):trace.append(name)
        def fetchone(self):
            if 'from RRL_CASE_PICK_EVENT'in self.calls[-1]:return(7,'CLOSED','picker',json.dumps({'request':request,**saved}))
            return super().fetchone()
    cursor=NativeCursor()
    class Gateway:
        @contextmanager
        def transaction(self,purpose):
            try:yield cursor
            except Exception:trace.append('rollback');raise
            else:trace.append('commit')
    with pytest.raises(HTTPException)as error:adapter.CaseCurrentClose(Gateway()).close(7,body,'picker')
    assert error.value.status_code==503 and error.value.detail['code']=='CASE_CURRENT_CLOSE_ACK_INVALID'
    assert trace[-1]=='rollback'and 'commit'not in trace
    assert 'RRL_CASE_LIFECYCLE_API.assert_new_close'not in trace
    assert not any('update 'in sql.lower()or 'insert 'in sql.lower()for sql in cursor.calls)


@pytest.mark.parametrize('raw', ['null', '[]', 'true', '42', '"saved"'])
def test_invalid_saved_envelope_is_conflict_not_new_execution(raw):
    from app.modules.inventory.infrastructure.case_close_journal import close_replay
    class SavedCursor:
        def execute(self,*args,**kwargs):pass
        def fetchone(self):return(7,'CLOSED','picker',raw)
    with pytest.raises(HTTPException)as error:
        close_replay(SavedCursor(),'CLOSE:1',7,'picker',{})
    assert error.value.status_code==409 and error.value.detail=='CASE_CLOSE_CONTENT_CONFLICT'
