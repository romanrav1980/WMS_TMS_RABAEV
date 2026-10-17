"""Assembly identity is rechecked inside the shared native close UOW."""
from pathlib import Path
from contextlib import contextmanager
import sys
import pytest
from fastapi import HTTPException
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.inventory.infrastructure import assembly_close as owner
from app.modules.inventory.infrastructure import case_current_close as current
from app.modules.inventory.contracts_assembly_close import AssemblyCloseInput
from app.modules.inventory.contracts_case_current_close import CaseCurrentCloseInput


class Gateway:
    @contextmanager
    def transaction(self,_):
        class ReadCursor(str):
            def execute(self,sql):assert sql=='set transaction read only'
        yield ReadCursor('INITIAL_READ')


@pytest.mark.parametrize('task,operator,expected',[(7,'operator',200),(8,'operator',403),(7,'other',403)])
def test_current_locked_session_binding_and_unchanged_ack(monkeypatch,task,operator,expected):
    scopes=[];reads=[]
    service=owner.AssemblyClose(Gateway(),lambda *args:scopes.append(args))
    def session(cursor,session_id,actor):
        reads.append(cursor)
        return dict(task_id=7,operator_id='operator')if cursor=='INITIAL_READ'else dict(task_id=task,operator_id=operator)
    monkeypatch.setattr(service,'_session',session)
    class Close:
        def __init__(self,gateway):pass
        def close(self,task_id,body,actor,assert_binding):
            assert isinstance(body,CaseCurrentCloseInput)and task_id==7 and actor=='operator'
            assert_binding('LOCKED_NATIVE_UOW',task_id,actor,'case_pick_execute')
            return dict(case_pick_task_id=7,operation_id=body.operation_id,status='WAIT_CONTROL',content_version=2,already_closed=False,physical_stock_changed=False)
    monkeypatch.setattr(owner,'CaseCurrentClose',Close)
    body=AssemblyCloseInput(operation_id='ASM.CLOSE.1',expected_content_version=2)
    if expected==403:
        with pytest.raises(HTTPException)as error:service.close('SESSION',body,'operator')
        assert error.value.status_code==403 and not scopes
    else:
        result=service.close('SESSION',body,'operator')
        assert result['session_id']=='SESSION'and result['operation_id']=='ASM.CLOSE.1'and result['physical_stock_changed']is False
        assert scopes==[('LOCKED_NATIVE_UOW',7,'operator','case_pick_execute')]
    assert reads==['INITIAL_READ','LOCKED_NATIVE_UOW']


def test_shared_close_runs_native_fence_before_optional_binding(monkeypatch):
    events=[]
    class Cursor:
        def callproc(self,name,args=()):events.append(name)
    class G:
        @contextmanager
        def transaction(self,_):
            try:yield Cursor()
            finally:events.append('UOW_END')
    def close(g,task,request,assert_scope,metadata_context,assert_new,validate_result):
        with metadata_context(g,'test',request.actor,'case_pick_execute')as cur:
            assert_scope(cur,task,request.actor,'case_pick_execute')
            events.append('WOULD_WRITE')
        return dict(status='WAIT_CONTROL',content_version=2,already_closed=False,physical_stock_changed=False)
    def deny(*args):
        events.append('SESSION_BINDING');raise HTTPException(403,'changed session')
    monkeypatch.setattr(current,'close_case_carrier',close)
    with pytest.raises(HTTPException):current.CaseCurrentClose(G()).close(7,CaseCurrentCloseInput(operation_id='OP',expected_content_version=2),'operator',assert_binding=deny)
    assert events==['RRL_CASE_LIFECYCLE_API.begin_close','RRL_CASE_LIFECYCLE_API.task_current_scope','SESSION_BINDING','RRL_CASE_LIFECYCLE_API.end_close','UOW_END']
