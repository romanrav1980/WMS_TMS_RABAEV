exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
from app.modules.finance.infrastructure.reconciliation_external_documents import external_documents,SOURCES
from app.modules.finance.infrastructure.reconciliation_erp import erp_snapshot
from app.modules.finance.infrastructure.reconciliation_regulatory import regulatory_snapshot
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute('set transaction read only');q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 for ware in [9807,31217707,38542432]:
  erp=erp_snapshot(q,ware);reg=regulatory_snapshot(q,ware)
  counts={'external_erp_ack_pending':sum(r['count']for r in erp),'regulatory_ack_not_reconciled':reg['message_count'],'regulatory_stock_source_unverified':reg['source_operation_unverified_count']}
  t=time.perf_counter();docs=external_documents(q,ware,counts);elapsed=time.perf_counter()-t
  for key,details in docs.items():
   ident,_,source=SOURCES[key];q.execute('select '+ident+' '+source+' order by '+ident,ware=ware);expected=[str(row[0])for row in q.fetchall()]
   assert details['document_ids']==expected[:20] and len(expected)==counts[key] and details['has_more']==(len(expected)>20)
  result[str(ware)]={'counts':counts,'documents':docs,'seconds':round(elapsed,3)}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30)as client:
 for ware in [9807,31217707,38542432]:
  r=client.get('/api/finance/day-reconciliation/warehouses/'+str(ware),params={'business_date':'2026-10-14','timezone_region':'UTC'});r.raise_for_status();data=r.json()
  result[str(ware)]['http_documents']={item['code']:item['documents']for item in data['open_items']if item['code']in SOURCES}
  assert result[str(ware)]['http_documents']==result[str(ware)]['documents']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT like 'select ''external_erp_ack_pending'' METRIC,DOCUMENT_ID from%' order by LAST_ACTIVE_TIME desc fetch first 5 rows only");result['sql']=q.fetchall()
Path('tmp/result1401.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:{'counts':v['counts'],'seconds':v['seconds']}if k!='sql'else v for k,v in result.items()}))