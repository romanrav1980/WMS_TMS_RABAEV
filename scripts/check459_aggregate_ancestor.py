exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
origin="100007031097593489"
box1="10385679679c3c81157494df2be36bc8e6bb367bb93d87f9331898ae6a6a4119"
pallet="1dd6fe2aeadccb35f8a1bfe45a8da1d7679546405c0f9e3833e517e98983c59a"
box2="91a875a766622153b6a238dbcc3cbfbc42edb6616db822f6e86d15eb20d354c7"
body=dict(system_code="CRPT",profile_code="TOBACCO",code_hash=box1,origin_pallet_identifier=origin,warehouse_id=10828603,reason_code="OPENED",document_reference="DEV459:open-first-box")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","trace_manifest_import"])
 try:
  out=q.var(oracledb.DB_TYPE_CLOB);q.setinputsizes(body=oracledb.DB_TYPE_CLOB)
  q.execute("begin :result:=RRL_TRACE_AGG_LIFECYCLE.invalidate(:op,:body,:actor);end;",result=out,op="AGG459.OPEN:BOX1",body=json.dumps(body,sort_keys=True,separators=(",",":")),actor="admin")
  result=read_oracle_json(out.getvalue())
  assert result["blocked_aggregate_count"]==2,result
  assert {x["code_hash"]for x in result["blocked_aggregates"]}=={box1,pallet},result
  for code in [box1,pallet]:
   try:q.callproc("RRL_TRACE_AGG_LIFECYCLE.assert_scan",["CRPT","TOBACCO",code])
   except oracledb.DatabaseError as e:assert e.args[0].code==20886 and "LOCAL_AGGREGATION_INVALIDATED"in str(e),str(e)
   else:raise AssertionError("Invalidated aggregate admitted")
  q.callproc("RRL_TRACE_AGG_LIFECYCLE.assert_scan",["CRPT","TOBACCO",box2])
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=origin);assert q.fetchone()==(3,0)
  c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_TRACE_AGG_BLOCK where ORIGIN_UID=:origin",origin=origin);assert q.fetchone()[0]==0
 q.callproc("RRL_TRACE_AGG_LIFECYCLE.assert_scan",["CRPT","TOBACCO",pallet])
 print("PASS459 unscanned original BOX1 cancellation blocks exact original PALLET, BOX2 remains unblocked; native scan guard; rollback restores 0 facts/3EA")
