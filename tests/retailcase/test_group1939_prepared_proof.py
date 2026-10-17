"""No Oracle imports/connections/ACL execution: frozen GROUP1939 recovery fault tests."""
import copy
import hashlib
import importlib.util
import json
from datetime import datetime,timezone
from pathlib import Path
import sys
import types
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'api/wms_api_server'))
spec=importlib.util.spec_from_file_location('group1939_quantity',ROOT/'tmp/group1939_quantity.py')
proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)


def journal():
    stamp=datetime(2026,10,15,18,0,tzinfo=timezone.utc)
    original=[dict(assignment_id='N1939.'+name,username=proof.ACTOR,role_id=proof.ROLE,scope_kind=kind,scope_id=scope,membership='CURRENT',snapshot_version=None,version_no=1,valid_from='2026-10-15T17:00:00.123456+00:00',valid_until='2026-10-15T22:11:39.774491+00:00')for name,kind,scope in [('SELF','SELF',None),('WARE','WAREHOUSE','13583852')]]
    from app.modules.inventory.contracts_stock import StockCommand
    wire=StockCommand(proof.OPERATION,'CASE_PICK_CONFIRM',proof.ACTOR,(),{'case_task_id':1139,'case_line_id':1141},metadata={'fact_qty':'1','scan_cell':'QIPcdbf4c0962','scan_product':'REUSE.QA:cdbf4c0962','scan_container':'090000000000010017','offline_event_id':None}).canonical_json()
    mapping=[dict(old_assignment_id=x['assignment_id'],new_assignment_id='N1939.GQP.RESTORE.'+('SELF'if x['scope_kind']=='SELF'else'WARE'),original_scope={k:x[k]for k in('role_id','scope_kind','scope_id','membership','snapshot_version','valid_from','valid_until')})for x in original]
    return dict(prepared_at=stamp.isoformat(),original_grants=original,acl_replacement_map=mapping,commands=proof.command_plan(original,stamp),stock_wire=wire,stock_sha256=hashlib.sha256(wire.encode()).hexdigest(),baseline={'fixture':{'role':{'row':{'role_id':proof.ROLE,'version_no':3,'active':1}},'task':[{'assigned_to':proof.ACTOR,'assigned_resource_id':63,'resource_session_id':59,'picked_qty':0,'sscc':'090000000000010017'}]},'line':[{'case_pick_task_id':1139,'case_pick_line_id':1141,'cell_code':'QIPcdbf4c0962','articul':'REUSE.QA:cdbf4c0962','planned_qty':1,'picked_qty':0}]},history=[],steps={})


def test_valid_plan_restores_new_ids_exact_original_expiry_and_records_old_mapping():
    value=journal();proof.validate_journal(value)
    assert {row['new_assignment_id']for row in value['acl_replacement_map']}=={'N1939.GQP.RESTORE.SELF','N1939.GQP.RESTORE.WARE'}
    for suffix in ['SELF','WARE']:
        restored=value['commands']['restore_'+suffix]['command']['payload']
        assert restored['expected_version']==0 and restored['valid_until']=='2026-10-15T22:11:39.774491+00:00'


@pytest.mark.parametrize('target,field,value',[('restore_WARE','role_id','OTHER'),('restore_SELF','username','admin'),('group_create','group_id','FOREIGN'),('group_assign','membership','SNAPSHOT')])
def test_rehashed_retargeting_cannot_change_frozen_commands(target,field,value):
    data=journal();item=data['commands'][target];item['command']['payload'][field]=value
    item['wire']=json.dumps(item['command'],ensure_ascii=False,sort_keys=True,separators=(',',':'));item['sha256']=hashlib.sha256(item['wire'].encode()).hexdigest()
    with pytest.raises(AssertionError,match='retargeted'):proof.validate_journal(data)


def test_rehashed_quantity_retarget_and_changed_cleanup_mapping_are_rejected():
    value=journal();changed=copy.deepcopy(value)
    body=json.loads(changed['stock_wire']);body['metadata']['fact_qty']='2';changed['stock_wire']=json.dumps(body,sort_keys=True,separators=(',',':'));changed['stock_sha256']=hashlib.sha256(changed['stock_wire'].encode()).hexdigest()
    with pytest.raises(AssertionError,match='retargeted'):proof.validate_journal(changed)
    value['acl_replacement_map'][0]['new_assignment_id']='admin'
    with pytest.raises(AssertionError,match='mapping retargeted'):proof.validate_journal(value)


def test_foreign_original_revoke_is_not_undone_without_our_immutable_receipt(monkeypatch):
    data=journal();attempts=[]
    monkeypatch.setattr(proof,'fixture',lambda *a,**k:{})
    monkeypatch.setattr(proof,'save',lambda *_:None)
    monkeypatch.setattr(proof,'original_source',lambda g,item:{'revoked_at':'foreign','version_no':2})
    monkeypatch.setattr(proof,'own_receipt',lambda *args:True)
    monkeypatch.setattr(proof,'run_acl',lambda g,j,name,compensation=False:attempts.append(name))
    class Gateway:
        def fetch_all(self,sql,*args):return []if 'RRL_PLATFORM_COMMAND'in sql else[{'owned':True}]
    with pytest.raises(RuntimeError,match='restoration incomplete'):proof.restore(Gateway(),data)
    assert attempts==['group_revoke','group_retire']


def test_foreign_private_group_is_not_retired_after_create_collision(monkeypatch):
    data=journal();attempts=[]
    monkeypatch.setattr(proof,'fixture',lambda *a,**k:(_ for _ in()).throw(RuntimeError('fixture changed')))
    monkeypatch.setattr(proof,'save',lambda *_:None)
    monkeypatch.setattr(proof,'own_receipt',lambda *args:False)
    monkeypatch.setattr(proof,'run_acl',lambda *args,**kw:attempts.append(args))
    class Gateway:
        def fetch_all(self,*args):return [{'foreign':True}]
    with pytest.raises(RuntimeError,match='restoration incomplete'):proof.restore(Gateway(),data)
    assert attempts==[] and data['status']=='RECOVERY_REQUIRED'


def test_fixture_and_disk_failure_still_attempt_owned_private_cleanup(monkeypatch):
    data=journal();attempts=[]
    monkeypatch.setattr(proof,'fixture',lambda *a,**k:(_ for _ in()).throw(RuntimeError('fixture changed')))
    monkeypatch.setattr(proof,'save',lambda *_:(_ for _ in()).throw(OSError('disk full')))
    monkeypatch.setattr(proof,'own_receipt',lambda *args:True)
    monkeypatch.setattr(proof,'run_acl',lambda g,j,name,compensation=False:attempts.append((name,compensation)))
    class Gateway:
        def fetch_all(self,*args):return [{'owned':True}]
    with pytest.raises(RuntimeError,match='restoration incomplete'):proof.restore(Gateway(),data)
    assert attempts==[('group_revoke',True),('group_retire',True)]


def test_disk_failure_does_not_skip_already_frozen_compensation_and_ack_is_checked(monkeypatch):
    data=journal();attempts=[]
    class Owner:
        def __init__(self,g):pass
        def command(self,actor,command):
            attempts.append((actor,command));p=command['payload']
            return dict(operation_id=command['operation_id'],command_type=command['command_type'],object_id=p['assignment_id'],version=2,replayed=False)
    module=types.ModuleType('app.modules.platform.public');module.AccessMetadataService=Owner
    monkeypatch.setitem(sys.modules,'app.modules.platform.public',module)
    monkeypatch.setattr(proof,'save',lambda *_:(_ for _ in()).throw(OSError('disk full')))
    proof.run_acl(object(),data,'group_revoke',True)
    assert len(attempts)==1 and data['logging_errors']and data['ack_sha256']['group_revoke']


def test_default_plan_does_not_import_oracle_or_write_journal(monkeypatch,capsys):
    monkeypatch.setattr(sys,'argv',['runner','--plan'])
    monkeypatch.setattr(proof,'save',lambda *_:pytest.fail('Plan wrote journal'))
    proof.main()
    result=json.loads(capsys.readouterr().out)
    assert result['status']=='PREPARED_NOT_EXECUTED'and result['fixture']['resource']==63 and result['fixture']['session']==59


def test_original_source_expiry_change_is_rejected_before_restore():
    value=journal()['original_grants'][0]
    row=dict(value,valid_until='2026-10-16T22:11:39.774491+00:00',revoked_at='owned')
    class Gateway:
        def fetch_all(self,*args):return [row]
    with pytest.raises(AssertionError,match='identity/scope/validity changed'):proof.original_source(Gateway(),value)
