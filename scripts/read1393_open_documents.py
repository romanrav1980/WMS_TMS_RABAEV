exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.reconciliation_documents import backlog_documents
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select FROM_WARE_ID,count(*) from RRL_WAREHOUSE_TASK where STATUS not in('DONE','CANCELLED')and FROM_WARE_ID is not null group by FROM_WARE_ID order by count(*)desc fetch first 1 rows only");row=q.fetchone()
 q.execute("select c.CASE_ID,l.WARE_ID from RRL_STORE_DISCREPANCY_CASE c join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=c.LOAD_OPERATION_ID where c.STATUS!='CLOSED' fetch first 1 rows only");case=q.fetchone()
 result={'tasks':row,'case':case}
 if row:
  counts,details=backlog_documents(q,int(row[0]));result['task_samples']=details['open_warehouse_tasks'];result['task_total']=counts['open_warehouse_tasks']
 print(json.dumps(result));Path('tmp/context1393.json').write_text(json.dumps(result,indent=2),encoding='utf-8')