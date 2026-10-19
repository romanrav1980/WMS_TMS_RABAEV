"""Resume owned IN_TRANSIT40 native wave and CASE; no physical seed."""
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
PATH=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T07/transit40.json'
s=json.loads(PATH.read_text())if PATH.exists()else dict(warehouse_id=215590763,order_id=2186,plan_id=2237,quantity=40,history=[])
def save():PATH.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def run():
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 if 'wave_id'not in s:
  s['wave_id']=expect(200,http('POST','/api/picking/waves',dict(wave_code='T7.TRANSIT40.V2',wave_name='TRADECASE IN_TRANSIT QA',ware_id=s['warehouse_id'],planned_start_at='2026-11-01T08:00:00+03:00',planned_finish_at='2026-11-01T09:00:00+03:00')))['pick_wave_id'];save()
 base=f"/api/picking/waves/{s['wave_id']}"
 for key,path,body in [('plan_added','/plans',dict(pick_plan_id=s['plan_id'])),('calculated','/calculate',{}),('launched','/launch',dict(operation_id='T7.TRANSIT40.LAUNCH.V2')),('released','/release-picking',dict(operation_id='T7.TRANSIT40.RELEASE'))]:
  if key not in s:s[key]=expect(200,http('POST',base+path,body));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w',w=s['wave_id']);rows=q.fetchall();assert len(rows)==1,rows;s['case_id'],s['line_id'],s['pick_task_id']=rows[0];save()
 print(json.dumps(s,default=str)[:1800])
if __name__=='__main__':
 try:run();s['stage']='WAVE_READY'
 except Exception as e:s['stage']='FAIL';s['error']=str(e);raise
 finally:s['history']+=CALLS;save()
