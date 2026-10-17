"""Prepared runner safety checks with no Oracle imports, connections or ACL execution."""
import copy
import hashlib
import json
import sys
import types
from datetime import datetime,timezone
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'api/wms_api_server'))
from scripts import case_group_quantity_proof as proof


def journal():
    stamp=datetime(2026,10,15,15,10,tzinfo=timezone.utc)
    original=[dict(assignment_id='CRES15.'+name,username=proof.ACTOR,role_id=proof.ROLE,scope_kind=kind,scope_id=scope,membership='CURRENT',snapshot_version=None,version_no=1,valid_from='2026-10-15T13:00:00.000000+00:00',valid_until='2026-10-15T16:26:48.000000+00:00')for name,kind,scope in [('SELF','SELF',None),('WARE','WAREHOUSE','13583852')]]
    from app.modules.inventory.contracts_stock import StockCommand
    wire=StockCommand(proof.OPERATION,'CASE_PICK_CONFIRM',proof.ACTOR,(),{'case_task_id':1138,'case_line_id':1140},metadata={'fact_qty':'1','scan_cell':'QIPcdbf4c0962','scan_product':'REUSE.QA:cdbf4c0962','scan_container':'090000000000009028','offline_event_id':None}).canonical_json()
    return dict(prepared_at=stamp.isoformat(),original_grants=original,commands=proof.command_plan(original,stamp),stock_wire=wire,stock_sha256=hashlib.sha256(wire.encode()).hexdigest(),baseline={'fixture':{'role':{'row':{'role_id':proof.ROLE,'version_no':3,'active':1}},'task':[{'assigned_to':proof.ACTOR,'assigned_resource_id':59,'resource_session_id':55,'picked_qty':0,'sscc':'090000000000009028'}]},'line':[{'case_pick_task_id':1138,'case_pick_line_id':1140,'cell_code':'QIPcdbf4c0962','articul':'REUSE.QA:cdbf4c0962','planned_qty':1,'picked_qty':0}]},history=[],steps={})


def test_valid_frozen_plan_and_self_hashed_retargeting_rejected():
    value=journal();proof.validate_journal(value)
    for target,field,replacement in [('restore_WARE','role_id','OTHER.ROLE'),('restore_SELF','username','admin'),('group_create','group_id','OTHER.GROUP')]:
        changed=copy.deepcopy(value);frozen=changed['commands'][target];frozen['command']['payload'][field]=replacement
        frozen['wire']=json.dumps(frozen['command'],ensure_ascii=False,sort_keys=True,separators=(',',':'));frozen['sha256']=hashlib.sha256(frozen['wire'].encode()).hexdigest()
        with pytest.raises(AssertionError,match='retargeted'):proof.validate_journal(changed)


def test_frozen_physical_command_cannot_be_retargeted_even_with_new_hash():
    value=journal();body=json.loads(value['stock_wire']);body['source']['case_task_id']=1136;value['stock_wire']=json.dumps(body,sort_keys=True,separators=(',',':'));value['stock_sha256']=hashlib.sha256(value['stock_wire'].encode()).hexdigest()
    with pytest.raises(AssertionError,match='retargeted'):proof.validate_journal(value)


def test_fixture_failure_and_disk_failure_do_not_skip_private_group_cleanup(monkeypatch):
    value=journal();attempts=[]
    monkeypatch.setattr(proof,'fixture',lambda *a,**k:(_ for _ in()).throw(RuntimeError('Fixture retired')))
    monkeypatch.setattr(proof,'save',lambda *_:(_ for _ in()).throw(OSError('disk full')))
    monkeypatch.setattr(proof,'run_acl',lambda g,j,name,compensation=False:attempts.append((name,compensation)))
    class Gateway:
        def fetch_all(self,*args):return [{'owned':True}]
    with pytest.raises(RuntimeError,match='restoration incomplete'):proof.restore(Gateway(),value)
    assert attempts==[('group_revoke',True),('group_retire',True)]


def test_disk_failure_during_compensation_progress_still_attempts_exact_canonical_command(monkeypatch):
    value=journal();attempts=[]
    class Owner:
        def __init__(self,gateway):pass
        def command(self,actor,command):attempts.append((actor,command));return {'version':2}
    module=types.ModuleType('app.modules.platform.public');module.AccessMetadataService=Owner
    monkeypatch.setitem(sys.modules,'app.modules.platform.public',module)
    monkeypatch.setattr(proof,'save',lambda *_:(_ for _ in()).throw(OSError('disk full')))
    proof.run_acl(object(),value,'group_revoke',True)
    assert attempts==[('admin',value['commands']['group_revoke']['command'])]
    assert value['logging_errors']


def test_prepared_plan_mode_does_not_need_oracle_or_create_a_journal(monkeypatch,capsys):
    monkeypatch.setattr(sys,'argv',['runner','--plan'])
    monkeypatch.setattr(proof,'save',lambda *_:pytest.fail('Plan mode wrote journal'))
    proof.main()
    assert json.loads(capsys.readouterr().out)['status']=='PREPARED_NOT_EXECUTED'


def test_foreign_revoke_without_our_native_receipt_is_never_undone(monkeypatch):
    value=journal();attempts=[]
    monkeypatch.setattr(proof,'fixture',lambda *a,**k:{})
    monkeypatch.setattr(proof,'save',lambda *_:None)
    monkeypatch.setattr(proof,'original_source',lambda g,item:{'revoked_at':'external','version_no':2})
    monkeypatch.setattr(proof,'run_acl',lambda g,j,name,compensation=False:attempts.append(name))
    class Gateway:
        def fetch_all(self,sql,*args):return []if 'RRL_PLATFORM_COMMAND'in sql else[{'owned':True}]
    with pytest.raises(RuntimeError,match='restoration incomplete'):proof.restore(Gateway(),value)
    assert attempts==['group_revoke','group_retire']
