"""Bounded native admission, quantity and immutable-evidence verification."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07'
s=json.loads((OUT/'bulk-remainder.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'db/migrations/2026-10-22_trade_hu_defer_wait/manifest.json').read_text())
report=dict(checks=[],sources={})
with oracle_connection()as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
 q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0]==0
 for key,item in manifest.items():
  q.execute('select text from user_source where NAME=:n and TYPE=:t order by LINE',n=item['name'],t=item['type']);digest=hashlib.sha256(''.join(r[0]for r in q).replace('\r','').rstrip('\n').encode()).hexdigest().upper();assert digest==item['after'];report['sources'][key]=digest
 q.execute('select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1169');uid=q.fetchone()[0]
 request=dict(contract_version=2,operation_id='NATIVE_PROBE_NOT_POSTED',command_type='HU_PLAN_MOVE',actor='admin',source=dict(uid=s['root']),metadata=dict(defer_decision_operation_id='NB22.DEFER.B',target_cell=s['wait_cell_seeded']),lines=[],units=[])
 q.callproc('RRL_TRADE_STOCK_GUARD.assert_command_stock',[uid,json.dumps(request),'admin']);report['checks'].append('Registered same-order tree admitted by guard; no posting performed')
 def denied(label,value,stock=uid,actor='admin'):
  try:q.callproc('RRL_TRADE_STOCK_GUARD.assert_command_stock',[stock,json.dumps(value),actor])
  except Exception as exc:
   code=getattr(exc.args[0],'code',None);assert code in(20882,20886,20911),str(exc);report['checks'].append(dict(test=label,code=code,reason=str(exc).split('\n')[0]));return
  raise AssertionError('Expected native rejection: '+label)
 denied('Ordinary move without registered decision',dict(request,metadata=dict(target_cell=s['wait_cell_seeded'])))
 denied('Another root cannot borrow decision',dict(request,source=dict(uid='BULK22.PAL.STAGING.220793322')))
 denied('Another target cannot borrow decision',dict(request,metadata=dict(request['metadata'],target_cell=s['cell'])))
 q.execute('select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1161');foreign=q.fetchone()[0]
 denied('Other order outside selected tree',request,foreign)
 denied('Ordinary unplanned HU move remains forbidden',dict(request,command_type='HU_MOVE'))
 denied('Retired actor cannot replay native admission',request,actor=s['actor'])
 q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse']);report['stock']=list(q.fetchone());assert report['stock']==[7,5]
 q.execute("select UNIT_ID,PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,STOCK_STATUS from RRL_WMS_RECEIPT_UNIT where UID_PALLET='690000000630906379'order by UNIT_ID");report['units']=list(q)
 assert len({r[1]for r in report['units']})==10
 assert {r[0]for r in report['units']if r[4]=='ISSUED'}=={'7','8','9'}
 assert next(r for r in report['units']if r[0]=='1')[3]==s['wait_cell_seeded']
 q.execute('select ID,ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID in(641547,641548)order by ID');report['assignments']=list(q);assert [r[2]for r in report['assignments']]==[33665,33666]
 q.execute('select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=1224');assert q.fetchone()[0]=='DONE'
 operations=['NB22.LOAD.A','NB22.WAIT.PLAN.B','NB22.WAIT.COMPLETE.B']
 for op in operations:
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=op);assert q.fetchone()[0]==1
 q.execute("select CUSTOMER_ORDER_ID,SHIPMENT_DATE from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID in(2197,2198)order by CUSTOMER_ORDER_ID");report['original_dates']=list(q);assert all(r[1].strftime('%Y-%m-%d')=='2026-10-22'for r in report['original_dates'])
 q.execute("select LOG_ID,API_PATH,ELAPSED_MS,SQL_TEXT_HASH,ERROR_TEXT from RRL_SQL_SLOW_LOG where CREATED_AT>=cast(systimestamp as timestamp)-interval '1'hour and(API_PATH like '/api/receiving/st-deferrals/%'or API_PATH like '/api/transport/st-deferrals%'or API_PATH like '/api/warehouse-tasks/1224%')order by LOG_ID desc fetch first 30 rows only");report['slow_sql']=list(q)
 c.rollback()
report.update(status='PASS',sql_decision='Retain bounded native tree/locks. Review first-request latency in T12; no demonstrated new index requirement.',limitations=['Native guard probes do not replace concurrent full posting or scoped waiting API acceptance.','Provider documents and measures are synthetic.'])
(OUT/'bulk-remainder-verification.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps(dict(status=report['status'],checks=len(report['checks']),stock=report['stock'],slow_sql=report['slow_sql'])))
