exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
from app.modules.finance.infrastructure.reconciliation_stock_documents import stock_documents,SOURCES
from app.modules.finance.infrastructure.reconciliation_stock import stock_snapshot
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=30000;q=c.cursor();q.execute('set transaction read only');q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute('select distinct c.WARE_ID from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL order by c.WARE_ID fetch first 60 rows only');wares=[r[0]for r in q.fetchall()]
 for ware in wares:
  stock=stock_snapshot(q,ware);counts={'stock_quantity_invariants':sum(int(r['invalid_rows']or 0)for r in stock['by_base_uom']),'physical_unit_composition':stock['physical_unit_composition_conflicts']}
  if not any(counts.values()):continue
  t=time.perf_counter();docs=stock_documents(q,ware,counts);elapsed=time.perf_counter()-t
  for key,details in docs.items():
   q.execute('select cast(r.UID_POLETA as varchar2(160)),r.CELL '+SOURCES[key]+' order by r.UID_POLETA,r.CELL',ware=ware);expected=[json.dumps(list(row),ensure_ascii=False,separators=(',',':'))for row in q.fetchall()]
   assert details['document_ids']==expected[:20] and len(expected)==counts[key] and details['has_more']==(len(expected)>20)
  result[str(ware)]={'counts':counts,'documents':docs,'seconds':round(elapsed,3)}
  if len(result)>=3:break
 if not result:
  result['9807']={'counts':{'stock_quantity_invariants':0,'physical_unit_composition':0},'documents':stock_documents(q,9807,{'stock_quantity_invariants':1,'physical_unit_composition':1}),'forced_empty_query':True}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=45)as client:
 for ware,entry in result.items():
  r=client.get('/api/finance/day-reconciliation/warehouses/'+ware,params={'business_date':'2026-10-14','timezone_region':'UTC'});r.raise_for_status();data=r.json();entry['http_documents']={i['code']:i['documents']for i in data['open_items']if i['code']in SOURCES}
  if not entry.get('forced_empty_query'):assert entry['http_documents']==entry['documents']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and (SQL_TEXT like 'select ''stock_quantity_invariants'' METRIC,UID_PALLET%' or SQL_TEXT like 'select ''physical_unit_composition'' METRIC,UID_PALLET%') order by LAST_ACTIVE_TIME desc fetch first 5 rows only");result['sql']=q.fetchall()
out=Path('reports/nicora/2026-10-13/codex/NI072');out.mkdir(parents=True,exist_ok=True);(out/'result_stock_keys.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))