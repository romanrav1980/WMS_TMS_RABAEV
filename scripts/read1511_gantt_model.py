exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from datetime import date
from app.modules.transport.infrastructure.gantt_rows import gantt_rows
class Capture:
 def fetch_all(self,sql,params):self.sql=sql;self.params=params;return []
cap=Capture();gantt_rows(cap,date(2026,10,15))
tt="(select 1 ID,cast(null as varchar2(30)) TRANSPORT,'20' TRANSTYPE,0 DELETED,date '2026-10-14' SHIPMENT_DATE from dual)"
vehicle="(select cast(null as varchar2(30)) NUM,0 ID from dual where 1=0)"
ops="""(select 1 TT_ID,1 ID,'DRIVE' OPERATION_CODE,1 ORD,120 DURATION_MIN,
 date '2026-10-14'+23/24 PLAN_START,date '2026-10-15'+1/24 PLAN_END,
 cast(null as date) FACT_START,cast(null as date) FACT_END,cast(null as varchar2(30)) NOTE from dual
 union all select 1,2,'END_AT_MIDNIGHT',2,60,date '2026-10-14'+23/24,date '2026-10-15',null,null,null from dual
 union all select 1,3,'OPEN_FACT',3,60,null,null,date '2026-10-14'+23/24,null,null from dual
 union all select 1,4,'POINT',4,0,date '2026-10-15',date '2026-10-15',null,null,null from dual
 union all select 1,5,'TOMORROW',5,60,date '2026-10-16',date '2026-10-16'+1/24,null,null,null from dual)"""
sql=cap.sql.replace('RRL_TRANSPORT_TASK TT',tt+' TT').replace('RRL_TR_VEHICLE V',vehicle+' V').replace('RRL_TT_OPERATIONS OPS',ops+' OPS')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute(sql,cap.params);names=[x[0] for x in q.description];rows=[dict(zip(names,r)) for r in q];assert {r['ID'] for r in rows}=={1,3,4}
Path('reports/nicora/2026-10-13/gantt_overlap_model1511.json').write_text(json.dumps({'kind':'read-only Oracle derived-table model using unchanged actual query predicate','included':[r['ID'] for r in rows],'cases':['cross-midnight included','exact end boundary excluded','open fact included','zero-duration point included','tomorrow excluded'],'writes':0},indent=2),encoding='utf-8')
print('PASS read-only Oracle model: cross-midnight, boundary, open fact, point, tomorrow')
