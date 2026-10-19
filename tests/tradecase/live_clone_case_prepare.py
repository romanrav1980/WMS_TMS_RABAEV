"""Prepare one real BEFORE_PICK unit from the BLC split clone, using native planning."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T06/clone-case.json');s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=211559882,source_uid='PART:H_PFDyPVMreJ5NtO89OXEXP9SA79NCol8OlsFXvW7pA',source_cell='T6X83fe97a6S',pick_cell='T6C.BLC.PICK',wait_cell='T6C.BLC.WAIT',article='TC0317CD4AAE',history=[])
def save():P.write_text(json.dumps(s,indent=2,default=str))
def run():
 w=s['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  if 'cells'not in s:
   q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=s['source_uid'],c=s['source_cell']);assert q.fetchone()==(1,0)
   q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('update RRL_CELLS set IS_SYSTEM=0 where CELL=:c and WARE_ID=:w',c=s['source_cell'],w=w)
    for cell,pick,system in [(s['pick_cell'],1,0),(s['wait_cell'],0,1),('CPT_'+str(w),0,1)]:
     q.execute('select count(*)from RRL_CELLS where CELL=:c',c=cell)
     if not q.fetchone()[0]:
      q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,:p,:s,0,0)',c=cell,w=w,p=pick,s=system)
      q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
    c.commit()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
   for cell,zone,owner in [(s['source_cell'],'STORAGE',None),(s['pick_cell'],'PICK','BLC'),(s['wait_cell'],'WAIT',None),('CPT_'+str(w),'SORT',None)]:
    q.execute('select nvl(max(VERSION_NO),0)from RRL_TRADE_CELL_POLICY where CELL=:c',c=cell);v=q.fetchone()[0]
    expect(200,http('PUT',base+'/stock/cells/'+cell,dict(operation_id='T6C.policy.'+cell,expected_version=v,zone_kind=zone,owner_id=owner,reason='Owned split clone picking proof')))
   s['cells']=True;save()
 if 'route'not in s:
  s['route']=expect(200,http('POST','/api/picking/routes',dict(route_code='T6C.BLC',route_name='Split clone QA',ware_id=w)))['pick_route_id'];save()
 if 'route_cell'not in s:s['route_cell']=expect(200,http('POST','/api/picking/route-cells',dict(pick_route_id=s['route'],cell_code=s['pick_cell'],pick_sequence=1)))['pick_route_cell_id'];save()
 if 'face'not in s:
  s['face']=expect(200,http('POST','/api/picking/pick-faces',dict(ware_id=w,cell_code=s['pick_cell'],pick_face_code='T6C.BLC',pick_route_id=s['route'],pick_route_cell_id=s['route_cell'],pick_sequence=1,min_case_qty=0,max_case_qty=100,replenishment_trigger_qty=1)))['pick_face_id'];save()
 if 'face_article'not in s:s['face_article']=expect(200,http('POST',f"/api/picking/pick-faces/{s['face']}/articuls",dict(articul=s['article'],priority='1',min_qty='0',max_qty='100',replenishment_method='IMMEDIATE',replenishment_qty_mode='FILL_TO_VOLUME',use_articul_replenish_rule=0,boxes_per_layer='5',boxes_per_pallet='25',box_volume_m3='0.01')));save()
 if 'customer'not in s:s['customer']=expect(200,http('POST','/api/customers',dict(customer_code='T6C.BLC',customer_name='Split clone QA',customer_type='LEGAL_ENTITY')))['customer_id'];save()
 if 'demand'not in s:
  def send(kind,id,payload):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='T6C.'+kind,source_id='TC03.SAP',warehouse_id=w,document_id=id,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload))))
  send('RECIPIENT','C.CLONE',dict(title='Split clone QA',wms_customer_id=s['customer'],target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0))
  send('ORDER','CLONE',dict(recipient_id='C.CLONE',planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='1',uom='EA',min_osg_days=0)]));s['demand']=True;save()
 if 'native_order'not in s:
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');s['native_order'],s['native_row']=q.fetchone()
    q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,'T6C.CLONE',:c,:w,to_date('2026-11-01','YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')",o=s['native_order'],c=s['customer'],w=w)
    q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Split clone QA','EA',1,:w,'OPEN','admin')",r=s['native_row'],o=s['native_order'],a=s['article'],w=w);c.commit()
   finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
  save()
 if 'bound'not in s:s['bound']=expect(200,http('POST',base+'/orders/CLONE/binding',dict(operation_id='T6C.bind',expected_order_version=1,customer_order_id=s['native_order'],lines=[dict(line_id='1',customer_order_row_id=s['native_row'])])));save()
 if 'plan'not in s:s['plan']=expect(200,http('POST','/api/picking/plans',dict(operation_id='T6C.plan.2',customer_order_id=s['native_order'])))['pick_plan_id'];save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select PICK_TASK_ID,PALLET_UID,SOURCE_CELL_CODE,QTY from RRL_PICK_TASK where PICK_PLAN_ID=:p',p=s['plan']);tasks=[list(r)for r in q];assert len(tasks)==1 and tasks[0][1]==s['source_uid']and tasks[0][3]==1,tasks;s['planned_tasks']=tasks
 if 'wave'not in s:s['wave']=expect(200,http('POST','/api/picking/waves',dict(wave_code='T6C.CLONE2',wave_name='Split clone QA',ware_id=w,planned_start_at='2026-11-01T08:00:00+03:00',planned_finish_at='2026-11-01T09:00:00+03:00')))['pick_wave_id'];save()
 for key,path,body in [('wave_plan','/plans',dict(pick_plan_id=s['plan'])),('calculated','/calculate',{}),('launched','/launch',dict(operation_id='T6C.launch.2'))]:
  if key not in s:s[key]=expect(200,http('POST',f"/api/picking/waves/{s['wave']}"+path,body));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute("select TASK_ID,STATUS,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w",w=s['wave']);s['replenishment_tasks']=[list(r)for r in q]
 s['status']='PLAN_WAVE_READY';s.pop('error',None);print(json.dumps(dict(status=s['status'],wave=s['wave'],tasks=s['replenishment_tasks'])))
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save()
