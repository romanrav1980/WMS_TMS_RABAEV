"""Native caller-rollback trials, then one explicit isolated TEST pick/close."""
from pathlib import Path
import sys,json,copy
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
from app.db import oracle_connection
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.infrastructure.assembly_close import AssemblyClose
from app.modules.inventory.contracts_assembly_close import AssemblyCloseInput
from app.modules.resources.public import assert_case_task_access
from fastapi import HTTPException
import oracledb
x=json.loads((f.BASE/'fixture.json').read_text());assert x['state']=='SCOPED_ASM_READY_NO_QUANTITY_COMMIT'
mass=json.loads((f.BASE/'test-mass-stage.json').read_text());data=mass['post_context']['command']
body=dict(contract_version=2,command_type='CASE_PICK_CONFIRM',lines=[],units=[],**data)
out=f.BASE/'pick-close-acceptance.json';resume='--resume-after-cell-publication'in sys.argv;g=f.OracleGateway()
if resume:
 report=json.loads(out.read_text());assert report['state']=='PREPARED'and'rollback_result'not in report
else:
 assert not out.exists();report=dict(state='PREPARED',hardware_verified=False,body=body,checks=[])
def save():out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');f.save(x)
if not resume:
 with out.open('x',encoding='utf-8')as stream:json.dump(report,stream)
def snapshot():
 return dict(stock=g.fetch_all('select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u or UID_POLETA in(select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t)order by UID_POLETA,CELL',{'u':x['source'],'t':x['task_id']}),task=g.fetch_all('select STATUS,CONTENT_VERSION,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',{'t':x['task_id']}),step=g.fetch_all('select STATE from RRL_ASSEMBLY_STEP where STEP_ID=:s',{'s':x['step']}),uses=g.fetch_all('select count(*)N from RRL_ASSEMBLY_STEP_USE where STEP_ID=:s',{'s':x['step']}))
def native(c,request):
 output=c.var(oracledb.DB_TYPE_CLOB);c.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(request,sort_keys=True,separators=(',',':')),request['actor'],output,None])
 if output.getvalue()is None:c.callproc('RRL_STOCK_POSTING_API.execute_prepared',[output])
 return read_oracle_json(output.getvalue())
before=snapshot()
if resume:assert report['before']==before
else:report['before']=before;save()
request=f.StockCommand(body['operation_id'],body['command_type'],body['actor'],(),body['source'],metadata=body['metadata'])
report['pick']=f.StockPosting().post(request);save()
report['replay']=f.StockPosting().post(request);assert report['replay']==report['pick'];save()
after=snapshot();assert after['task'][0]['picked_qty']==1 and after['step']==[dict(state='APPLIED')]and after['uses']==[dict(n=1)]
report['after_pick']=after;x['state']='ASM_PICK_APPLIED';save()
close=AssemblyClose(g,assert_case_task_access)
close_body=AssemblyCloseInput(operation_id=x['prefix']+'.CLOSE',expected_content_version=after['task'][0]['content_version'])
report['close_request']=close_body.model_dump();save()
report['close']=close.close(x['assembly_session'],close_body,x['actor']);save()
report['close_replay']=close.close(x['assembly_session'],close_body,x['actor']);assert report['close_replay']==report['close']
assert snapshot()['task'][0]['status']=='WAIT_CONTROL'
report['state']='PASS_NATIVE_SCOPED_ASM_PICK_CLOSE_REPLAY';x['state']='SCOPED_ASM_CLOSED_WAIT_FINAL';save()
print(json.dumps(dict(state=report['state'],task=x['task_id'],checks=len(report['checks']),hardware_verified=False)))
