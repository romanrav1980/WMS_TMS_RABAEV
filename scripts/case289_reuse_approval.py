exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import uuid,copy
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID='RET231.LEGACY:13508027ed'and STATE='APPLIED'")
 old=read_oracle_json(q.fetchone()[0]);request=copy.deepcopy(old)
 request["operation_id"]="QA289."+uuid.uuid4().hex[:12];request["actor"]="admin"
 request["metadata"].update({"quantity":"1","disposition":"REUSE","complete_good_box":True,"reason":"Изолированный отказ раннего допуска неподтверждённой исходной партии","decision_reference":"Own289 existing original source"})
 c.rollback();out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request,ensure_ascii=False),"admin",out,None])
 except oracledb.DatabaseError as e:assert e.args[0].code==20886 and "RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED"in str(e),str(e)
 else:raise AssertionError("Legacy batch admitted for REUSE")
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=:operation_id",operation_id=request["operation_id"]);assert q.fetchone()==(0,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets from V$SQL
 where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%MIN(SUPPLIER_BATCH)%RRL_SAP_PALLET_RECEIPT%'or SQL_TEXT like '%min(SUPPLIER_BATCH)%RRL_SAP_PALLET_RECEIPT%')
 order by last_active_time desc fetch first 3 rows only""");print("SQL289_MS",q.fetchall())
print("PASS289 actual original229 acceptedremaining1 legacybatch denied at nativeapproval before pickup/receipt; no approval/qty/P20H20. No eligibleunapproved verifiedBOX source; newpositivepreflight pending, existing107positive retained")
