"""Real Oracle reads of synthetic frozen trees; no load facts or physical quantities are written."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from app.modules.integrations.infrastructure.trade_route import _LOADS,_UNATTRIBUTED
report=dict(status='FAIL',checks=[],physical_writes=0,fixture='Synthetic JSON only; not evidence of physical nested loading')
with oracle_connection() as c:
 q=c.cursor();q.execute('set transaction read only')
 q.execute('select lot.LOT_UID,pl.CUSTOMER_ORDER_ROW_ID from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID where lot.CASE_PICK_TASK_ID in(1168,1169)order by lot.CASE_PICK_TASK_ID');places=q.fetchall();assert len(places)==2
 real_prefix=_LOADS.split(' leaves as(',1)[0]
 fake_prefix="with facts as(select 'SYNTHETIC_READ_ONLY' LOAD_OPERATION_ID,'DEPARTED' STATUS,cast(null as timestamp with time zone)CUSTODY_RELEASED_AT,:tree COMPOSITION_JSON from dual),\n"
 def read(nodes):
  value=json.dumps(dict(nodes=nodes))
  loads=_LOADS.replace(real_prefix,fake_prefix,1);missing=_UNATTRIBUTED.replace(real_prefix,fake_prefix,1)
  q.execute(loads,w=220793322,tree=value);rows=[list(r)for r in q]
  q.execute(missing,w=220793322,tree=value);return rows,q.fetchone()[0]
 nodes=[dict(uid='PAL.TEST',kind='CONTAINER',depth=0),dict(uid='CASE:1168',kind='CASE',depth=2),dict(uid='CASE:1169',kind='CASE',depth=3)]
 nodes += [dict(uid=uid,kind='STOCK',quantity=str(i+1),depth=i+3)for i,(uid,_)in enumerate(places)]
 rows,missing=read(nodes);assert sorted((int(x[0]),int(x[3]))for x in rows)==sorted((int(row),i+1)for i,(_,row)in enumerate(places));assert missing==0
 report['checks'].append('Nested leaves resolve both real order rows and use frozen quantities rather than live CASE totals')
 rows,missing=read(nodes+[dict(uid='UNKNOWN.FROZEN.LEAF',kind='STOCK',quantity='1')]);assert missing==1
 report['checks'].append('Unknown child marks the load incomplete')
 rows,missing=read([]);assert rows==[] and missing==1
 report['checks'].append('Empty frozen composition remains unknown')
 q.execute('select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1155 fetch first 1 row only');foreign=q.fetchone();assert foreign
 rows,missing=read([dict(uid=foreign[0],kind='STOCK',quantity='1')]);assert rows==[] and missing==1
 report['checks'].append('Foreign-warehouse CASE cannot borrow the selected trip warehouse')
 c.rollback()
report['status']='PASS';out=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T09/frozen-tree-read.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))