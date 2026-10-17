"""Owned fixture-only physical metadata negatives, clean command TX, restoration finally."""
import sys,json
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_native import RUNTIME,REPORT,state,intent,trial,rejected
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import stock_configuration_transaction
from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin


def run():
 g=OracleGateway();ctx=json.loads(RUNTIME.read_text());checks=[];original=state(g,ctx);body=intent(g,ctx,'START')
 def shift_ware(ware):
  with stock_configuration_transaction(g,'Owned QA shift physical warehouse negative and exact restore','admin','warehouse_settings_edit')as c:c.execute('update RRL_RESOURCE_SHIFT set WARE_ID=:ware where SHIFT_ID=:id',ware=ware,id=ctx['shift'])
 actual=g.fetch_all('select WARE_ID from RRL_RESOURCE_SHIFT where SHIFT_ID=:id',{'id':ctx['shift']})[0]['ware_id']
 try:
  shift_ware(ctx['foreign_ware'])
  trial(g,ctx,checks,'coherent_resource_and_shift_actual_warehouse_required',lambda c:rejected(c,ctx['task'],{**body,'operation_id':'TASK.SHIFT:'+uuid4().hex},ctx['actor'],'WTASK_PHYSICAL_WAREHOUSE_REQUIRED'))
 finally:shift_ware(actual)
 qualification=QualificationAdmin(g)
 try:
  qualification.set_qualification(ctx['resource'],'PUTAWAY',False,'admin')
  trial(g,ctx,checks,'current_native_resource_qualification_required',lambda c:rejected(c,ctx['task'],{**body,'operation_id':'TASK.QUAL:'+uuid4().hex},ctx['actor'],'TASK_RESOURCE_QUALIFICATION_REQUIRED'))
 finally:qualification.set_qualification(ctx['resource'],'PUTAWAY',True,'admin')
 assert state(g,ctx)==original
 (REPORT/'physical-guards.json').write_text(json.dumps(dict(status='PASS',checks=checks,only_owned_fixture_metadata_temporarily_committed=True,shift_warehouse_exactly_restored=True,qualification_active_restored=True,command_receipts_events_task_version='CALLER_ROLLBACK_UNCHANGED',goods_commit=False),indent=2),encoding='utf-8');print('TASK_NATIVE_PHYSICAL_GUARDS_2_PASS')


if __name__=='__main__':run()
