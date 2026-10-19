"""Resumable native CASE pick and WAIT movement on the owned wave595 fixture."""
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T06';PATH=OUT/'case-1155.json'
state=json.loads(PATH.read_text())if PATH.exists()else dict(warehouse_id=215590763,case_id=1155,line_id=1157,pick_task_id=2166,wait_cell='T6W554eebf3',history=[])
def save():PATH.write_text(json.dumps(state,indent=2,default=str),encoding='utf-8')
def run():
 w=state['warehouse_id'];task=state['case_id'];line=state['line_id'];base=f'/api/tradecase/warehouses/{w}/stock'
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  for target_cell,system in [(state['wait_cell'],1),('CPT_'+str(w),1)]:
   q.execute('select count(*)from RRL_CELLS where CELL=:cell',cell=target_cell)
   if q.fetchone()[0]==0:
    q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
    try:
     q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,0,:s,0,0)',cell=target_cell,w=w,s=system)
     q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target_cell);c.commit()
    finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  for cell,zone in [(state['wait_cell'],'WAIT'),('CPT_'+str(w),'SORT')]:
   q.execute('select count(*)from RRL_TRADE_CELL_POLICY where CELL=:c',c=cell)
   if not q.fetchone()[0]:expect(200,http('PUT',base+'/cells/'+cell,dict(operation_id='T6.case.policy.'+cell,expected_version=0,zone_kind=zone,reason='Owned TRADECASE CASE acceptance location')))
  if 'tare_count'not in state:
   state['tare_count']=expect(200,http('POST','/api/inventory/tare/count',dict(operation_id='T6.tare.count.1155',owner_ware_id=w,pallet_type_id=1,condition='GOOD',observed_quantity='1',expected_version=0,reason='Simulated isolated QA pallet count, no physical survey claim',decision_reference='TEST_FIXTURE_NOT_HARDWARE:T6.1155')));save()
  if 'tare_book'not in state:
   state['tare_book']=expect(200,http('POST','/api/inventory/tare/book',dict(operation_id='T6.tare.book.1155',place_kind='CASE',place_id=str(task),expected_warehouse_id=w,pallet_type_id=1)));save()
  q.execute('select STATUS,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=task);status,carrier,version=q.fetchone()
  if status in ['NEW','ASSIGNED']:expect(200,http('POST',f'/api/case-pick/tasks/{task}/start',{}))
  if 'pick_body'not in state:
   q.execute("select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_LINE_ID=:p and r.STATUS in('ACTIVE','ALLOCATED','PICKING')order by u.UNIT_ID",p=state['pick_task_id'])
   scans=[dict(system_code=s,profile_code='TOBACCO',code=raw.read()if hasattr(raw,'read')else raw)for s,raw in q];assert len(scans)==100,len(scans)
   state['pick_body']=dict(operation_id='T6.case.pick.1155',fact_qty='100',scan_cell='T3P554eebf3',scan_product='TC03554EEBF3',scan_container=carrier,unit_scans=scans);save()
 if 'picked'not in state:
  state['picked']=expect(200,http('POST',f'/api/case-pick/tasks/{task}/lines/{line}/confirm',state['pick_body']));save()
 assert expect(200,http('POST',f'/api/case-pick/tasks/{task}/lines/{line}/confirm',state['pick_body']))==state['picked']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select STATUS,PICKED_QTY,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=task);status,qty,version=q.fetchone();assert qty==100,(status,qty,version)
 if 'closed'not in state:
  state['close_body']=dict(operation_id='T6.case.close.1155',expected_content_version=version);save()
  state['closed']=expect(200,http('POST',f'/api/case-pick/tasks/{task}/close-pallet',state['close_body']));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select STATUS,CONTENT_VERSION,SSCC,CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=task);status,version,carrier,cell=q.fetchone();state['closed_status']=status
 if 'moved'not in state:
  state['move_body']=dict(operation_id='T6.case.wait.1155',scan_container=carrier,scanned_to_cell=state['wait_cell'],expected_content_version=version);save()
  state['moved']=expect(200,http('POST',f'/api/case-pick/tasks/{task}/move-carrier',state['move_body']));save()
 assert expect(200,http('POST',f'/api/case-pick/tasks/{task}/move-carrier',state['move_body']))==state['moved']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN',w=w);rows=[list(r)for r in q];assert [r[2]for r in rows]==[100,150],rows;assert rows[0][1]==state['wait_cell'],rows;state['stock']=rows
  q.execute('select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY join RRL_CASE_CARRIER_LOT h on h.LOT_UID=u.CURRENT_UID where h.CASE_PICK_TASK_ID=:t',t=task);assert q.fetchall()==[('SNS',)]
 state['status']='PASS';state.pop('error',None)
if __name__=='__main__':
 try:run()
 except Exception as e:state['status']='FAIL';state['error']=str(e);raise
 finally:state['history']+=CALLS;save();print(json.dumps(dict(status=state.get('status'),file=str(PATH),http_calls=len(CALLS))))
