exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
origin="100007031097593489"
box="91a875a766622153b6a238dbcc3cbfbc42edb6616db822f6e86d15eb20d354c7"
pallet="1dd6fe2aeadccb35f8a1bfe45a8da1d7679546405c0f9e3833e517e98983c59a"
body=dict(system_code="CRPT",profile_code="TOBACCO",code_hash=box,origin_pallet_identifier=origin,warehouse_id=10828603,reason_code="OPENED",document_reference="DEV469:second-box-trial")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","trace_manifest_import"])
 try:
  out=q.var(oracledb.DB_TYPE_CLOB);q.setinputsizes(body=oracledb.DB_TYPE_CLOB)
  q.execute("begin :result:=RRL_TRACE_AGG_LIFECYCLE.invalidate(:op,:body,:actor);end;",result=out,op="AGG469.TRIAL:BOX2",body=json.dumps(body,sort_keys=True,separators=(",",":")),actor="admin")
  r=read_oracle_json(out.getvalue());assert {x["code_hash"]for x in r["blocked_aggregates"]}=={box,pallet},r
  q.execute("select count(*)from RRL_TRACE_AGG_BLOCK where ORIGIN_UID=:origin",origin=origin);assert q.fetchone()[0]==3
  q.callproc("RRL_TRACE_AGG_LIFECYCLE.assert_scan",["EGAIS","ALCOHOL","3af2c2ab3d1293d6df65bbb1f388f8e313d6e45acc39c3954b8f0a921d04df40"])
  c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_TRACE_AGG_BLOCK where ORIGIN_UID=:origin",origin=origin);assert q.fetchone()[0]==2
 q.callproc("RRL_TRACE_AGG_LIFECYCLE.assert_scan",["CRPT","TOBACCO",box])
 print("PASS469 optimized single-manifest ancestor closure, existing blocked parent preserved, other profile untouched, rollback returns2 committed blocks")
