"""Prepare one real BEFORE_PICK unit from the BLC split clone, using native planning."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T06/clone-box10.json');s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=211559882,source_uid='PART:H_PFDyPVMreJ5NtO89OXEXP9SA79NCol8OlsFXvW7pA',source_cell='T6X83fe97a6S',pick_cell='T6C.BLC.PICK',wait_cell='T6C.BLC.WAIT',article='TC0317CD4AAE',history=[])
def save():P.write_text(json.dumps(s,indent=2,default=str))
def run():
 w=s['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 if 'demand'not in s:
  def send(kind,id,payload):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='T6B.'+kind,source_id='TC03.SAP',warehouse_id=w,document_id=id,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload))))
  send('ORDER','CLONE10',dict(recipient_id='C.CLONE',planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='10',uom='EA',min_osg_days=0)]));s['demand']=True;save()
 if 'native_order'not in s:
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');s['native_order'],s['native_row']=q.fetchone()
    q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,'T6B.CLONE10',:c,:w,to_date('2026-11-01','YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')",o=s['native_order'],c=s['customer'],w=w)
    q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Split clone QA','EA',10,:w,'OPEN','admin')",r=s['native_row'],o=s['native_order'],a=s['article'],w=w);c.commit()
   finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
  save()
 if 'bound'not in s:s['bound']=expect(200,http('POST',base+'/orders/CLONE10/binding',dict(operation_id='T6B.bind',expected_order_version=1,customer_order_id=s['native_order'],lines=[dict(line_id='1',customer_order_row_id=s['native_row'])])));save()
 if 'plan'not in s:s['plan']=expect(200,http('POST','/api/picking/plans',dict(operation_id='T6B.plan',customer_order_id=s['native_order'])))['pick_plan_id'];save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select PICK_TASK_ID,PALLET_UID,SOURCE_CELL_CODE,QTY from RRL_PICK_TASK where PICK_PLAN_ID=:p',p=s['plan']);tasks=[list(r)for r in q];assert len(tasks)==1 and tasks[0][1]==s['source_uid']and tasks[0][3]==10,tasks;s['planned_tasks']=tasks
 if 'wave'not in s:s['wave']=expect(200,http('POST','/api/picking/waves',dict(wave_code='T6B.CLONE10',wave_name='Split clone QA',ware_id=w,planned_start_at='2026-11-01T08:00:00+03:00',planned_finish_at='2026-11-01T09:00:00+03:00')))['pick_wave_id'];save()
 for key,path,body in [('wave_plan','/plans',dict(pick_plan_id=s['plan'])),('calculated','/calculate',{}),('launched','/launch',dict(operation_id='T6B.launch'))]:
  if key not in s:s[key]=expect(200,http('POST',f"/api/picking/waves/{s['wave']}"+path,body));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute("select TASK_ID,STATUS,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w",w=s['wave']);s['replenishment_tasks']=[list(r)for r in q]
 s['status']='PLAN_WAVE_READY';s.pop('error',None);print(json.dumps(dict(status=s['status'],wave=s['wave'],tasks=s['replenishment_tasks'])))
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save()
