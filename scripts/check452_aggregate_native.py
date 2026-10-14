exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
origin="100007031097593489";op="AGG452.INVALIDATE:MANIFEST124"
body=dict(system_code="EGAIS",profile_code="ALCOHOL",code_hash="3af2c2ab3d1293d6df65bbb1f388f8e313d6e45acc39c3954b8f0a921d04df40",origin_pallet_identifier=origin,warehouse_id=10828603,reason_code="OPENED",document_reference="DEV452:physical-aggregate-opened")
wire=json.dumps(body,sort_keys=True,separators=(",",":"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def snap():
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=origin);stock=q.fetchone()
  q.execute("select count(*)from RRL_EVENTS where UID_POLETA=:p_uid",p_uid=origin);events=q.fetchone()[0]
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=origin);codes=q.fetchone()[0]
  return(stock,events,codes)
 before=snap();c.rollback()
 def call(payload):
  out=q.var(oracledb.DB_TYPE_CLOB);q.setinputsizes(body=oracledb.DB_TYPE_CLOB)
  q.execute("begin :result:=RRL_TRACE_AGG_LIFECYCLE.invalidate(:op,:body,:actor);end;",result=out,op=op,body=payload,actor="admin")
  return read_oracle_json(out.getvalue())
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","trace_manifest_import"])
 try:
  r=call(wire);assert r["stock_changed"]is False and r["government_ack_created"]is False,r
  assert snap()==before,(snap(),before)
  assert call(wire)==r
  try:call(json.dumps({**body,"reason_code":"DAMAGED"},sort_keys=True,separators=(",",":")))
  except oracledb.DatabaseError as e:assert e.args[0].code==20864,str(e)
  else:raise AssertionError("different payload admitted")
  c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_TRACE_AGG_INVALIDATION where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0
 assert snap()==before;c.rollback()
 print("PASS452 full rollback/idempotency/content-conflict/stock-event-code unchanged",before)
