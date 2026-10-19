"""Pass QA credentials only in child environment, then record actual Oracle after UI write/retry."""
from pathlib import Path
import json,os,subprocess,sys
sys.path.insert(0,'.')
from tools.mcp.tms_mcp_server import oracle_connection
p=Path('runtime/test-evidence/tradecase/2026-10-19/T11/return-ui-fixture.json');s=json.loads(p.read_text());assert s['status']=='READY_FOR_ONE_UI_RETURN'
with oracle_connection()as c:
 q=c.cursor();q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=s['actor']);row=q.fetchone();assert row
 env=dict(os.environ,TRADECASE_UI_USER=s['actor'],TRADECASE_UI_PASSWORD=row[0])
result=subprocess.run(['node','tests/tradecase/return_ui_check.cjs'],env=env,check=False)
if result.returncode:raise SystemExit(result.returncode)
r=json.loads(p.with_name('return-ui-result.json').read_text());assert r['status']=='PASS';op=r['livePosts'][0]['operation_id']
with oracle_connection()as c:
 q=c.cursor();q.execute('select STATE,COMMAND_TYPE,ACTOR from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=op);assert list(q.fetchone())==['APPLIED','CASE_CARRIER_RETURN',s['actor']]
 q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id']);assert list(q.fetchone())==[250,0]
 q.execute('select count(*),min(a.OWNER_ID),max(a.OWNER_ID),min(u.CURRENT_CELL),max(u.CURRENT_CELL)from RRL_TRADE_CASE_RETURN_UNIT h join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=h.PHYSICAL_UNIT_KEY join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where h.RETURN_OPERATION=:o',o=op);assert list(q.fetchone())==[10,'BLC','BLC','T6C.BLC.PICK','T6C.BLC.PICK']
 q.execute('select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case_id']);assert q.fetchone()[0]=='CANCELLED'
s.update(status='PASS_UI_RETURN10_LOST_REPLY_RETRY',operation_id=op,final_stock=[250,0],returned_owner='BLC',returned_units=10);p.write_text(json.dumps(s,indent=2,default=str));print(json.dumps(dict(status=s['status'],operation_id=op,stock=s['final_stock'])))
