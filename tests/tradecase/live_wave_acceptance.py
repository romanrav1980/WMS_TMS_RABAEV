"""Durable native wave execution on an owned TRADECASE fixture; no foreign stock."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
SOURCE=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T04/planning-34343cd3.json'
f=json.loads(SOURCE.read_text())['fixture'];OUT=SOURCE.parent/('wave-'+f['tag']+'.json')
s=json.loads(OUT.read_text())if OUT.exists()else dict(warehouse_id=f['warehouse_id'],fixture_source=str(SOURCE.relative_to(ROOT)),status='RUNNING')
assert s['warehouse_id']==f['warehouse_id']
def save():s['http']=CALLS;snapshot=dict(s);OUT.write_text(json.dumps(snapshot,indent=2,default=str),encoding='utf-8')
try:
    with oracle_connection()as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=f['warehouse_id']);assert q.fetchone()[0]=='TRADECASE QA '+f['tag']
    if not s.get('wave_id'):
        s['wave_id']=expect(200,http('POST','/api/picking/waves',dict(wave_code='T4.'+f['tag'],wave_name='TRADECASE QA',ware_id=f['warehouse_id'],planned_start_at='2026-11-01T08:00:00+03:00',planned_finish_at='2026-11-01T09:00:00+03:00')))['pick_wave_id'];save()
    base=f"/api/picking/waves/{s['wave_id']}"
    if not s.get('plan_added'):
        expect(200,http('POST',base+'/plans',dict(pick_plan_id=f['after_plan'])));s['plan_added']=True;save()
    if not s.get('calculated'):
        expect(200,http('POST',base+'/calculate',{}));s['calculated']=True;save()
    body=dict(operation_id='T4.launch.'+f['tag']);s['launch_body']=body;save()
    s['launch_result']=expect(200,http('POST',base+'/launch',body));save()
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=f['warehouse_id']);s['stock']=list(q.fetchone());assert s['stock'][0]==250
        q.execute("select TASK_ID,TASK_TYPE,STATUS,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w order by TASK_ID",w=s['wave_id']);s['tasks']=[list(x)for x in q]
        q.execute("select RESERVATION_ID,BASE_QTY,RESERVATION_DOMAIN,UID_PALLET,CELL from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=s['wave_id']);s['reservations']=[list(x)for x in q]
        q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
    s['status']='PASS_LAUNCH';save();print(json.dumps({k:s[k]for k in['status','wave_id','stock','tasks','reservations']},default=str))
except Exception as e:s.update(status='FAIL',error=str(e));save();raise
