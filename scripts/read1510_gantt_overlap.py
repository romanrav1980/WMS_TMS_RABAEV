exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from datetime import date,timedelta
from time import perf_counter
from app.modules.transport.infrastructure.gantt_rows import gantt_rows
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 class ReadGateway:
  def fetch_all(self,sql,params):
   q.execute(sql,params);names=[x[0] for x in q.description];return [dict(zip(names,r)) for r in q.fetchall()]
 gateway=ReadGateway();started=perf_counter();rows=gantt_rows(gateway,date(2026,10,14));elapsed=round((perf_counter()-started)*1000,3)
 q.execute("select OPS.ID from RRL_TRANSPORT_TASK TT join RRL_TT_OPERATIONS OPS on OPS.TT_ID=TT.ID where nvl(TT.DELETED,0)=0 and TT.SHIPMENT_DATE>=date '2026-10-14' and TT.SHIPMENT_DATE<date '2026-10-15'")
 old={r[0] for r in q};assert old.issubset({r['ID'] for r in rows})
 q.execute("select OPS.ID,OPS.TT_ID,trunc(OPS.PLAN_START)+1 TARGET_DAY from RRL_TT_OPERATIONS OPS join RRL_TRANSPORT_TASK TT on TT.ID=OPS.TT_ID where nvl(TT.DELETED,0)=0 and OPS.PLAN_START is not null and OPS.PLAN_END>trunc(OPS.PLAN_START)+1 and (TT.SHIPMENT_DATE<trunc(OPS.PLAN_START)+1 or TT.SHIPMENT_DATE>=trunc(OPS.PLAN_START)+2) order by OPS.ID desc fetch first 1 rows only")
 crossing=q.fetchone();evidence={'current_day_rows':len(rows),'old_operation_count':len(old),'all_old_rows_preserved':True,'elapsed_ms':elapsed,'writes':0}
 if crossing:
  started=perf_counter();cross_rows=gantt_rows(gateway,crossing[2].date());assert crossing[0] in {r['ID'] for r in cross_rows}
  evidence['real_cross_midnight']={'operation_id':crossing[0],'trip_id':crossing[1],'display_day':str(crossing[2].date()),'included':True,'elapsed_ms':round((perf_counter()-started)*1000,3),'rows':len(cross_rows)}
 else:evidence['real_cross_midnight']='No existing candidate; no synthetic writes'
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like 'SELECT /* RETAILCASE_GANTT_DAY_OVERLAP */%' order by LAST_ACTIVE_TIME desc fetch first 2 rows only");evidence['sql']=q.fetchall()
Path('reports/retailcase/2026-10-13/gantt_day_overlap1510.json').write_text(json.dumps(evidence,indent=2,default=str),encoding='utf-8');print(json.dumps(evidence,default=str))
