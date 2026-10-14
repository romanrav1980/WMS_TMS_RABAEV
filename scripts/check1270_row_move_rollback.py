exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
preview=json.loads(Path("tmp/preview1267.json").read_text())
command={"contract_version":2,"operation_id":"ST.LAYOUT.DRY:"+uuid4().hex,"command_type":"ST_PREPARED_ROW_MOVE","actor":"admin",
 "source":{"order_id":2135,"row_id":preview["row_id"],"target_shipment_id":641508},"lines":[],"units":[],
 "metadata":{"expected_signature":preview["signature"],"reason":"Rollback check of retained prepared-row transfer"}}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=10000;q=c.cursor()
 def rows():
  q.execute("select ID,PALLET_UID,ARTICUL,QUANTITY,ORDER_WEIGHT,PACK_COUNT from RRL_SBORKA_PALLET_ROWS where PALLET_UID in('OP_SAP_2135_1','OP_SAP_2135_2')order by ID")
  return q.fetchall()
 before=rows();inp=q.var(oracledb.DB_TYPE_CLOB);out=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  raw=out.getvalue();result=json.loads(raw.read()if hasattr(raw,"read")else raw)
  actual=rows();assert len(actual)==2 and all(r[3]==18 and r[4]==12 and r[5]==3 for r in actual)
 finally:
  c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 assert rows()==before
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=command["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA in('B01.1238:c0c2a00c0b:1','B01.1238:c0c2a00c0b:2')");assert q.fetchone()==(36,36)
 evidence={"status":"ROLLBACK_PASS","before":before,"during":actual,"stock":36,"hard":36,"operation":command["operation_id"]}
 Path("tmp/result1270.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8");print(json.dumps(evidence))
