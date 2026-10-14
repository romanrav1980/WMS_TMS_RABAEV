exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
progress=json.loads(Path("tmp/source310_progress.json").read_text(encoding="utf-8"));tag=progress["tag"]
assert not Path("tmp/context310.json").exists()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SOURCE_LOAD_OPERATION_ID,TARGET_WARE_ID,TARGET_TT_ID,INBOUND_DOCK from RRL_INTERWARE_PLAN where OPERATION_ID=:op",op="IW310.PLAN:"+tag);source_load,target,target_trip,inbound=q.fetchone()
 q.execute("select a.SYSTEM_CODE,a.PROFILE_CODE,a.AGG_LEVEL,a.RAW_CODE from RRL_TRACE_SENDER_AGG a where a.MANIFEST_OPERATION_ID=:op and a.AGGREGATION_ID in('CRPT.P','EGAIS.B')order by a.SYSTEM_CODE",op="IW310.MANIFEST:"+tag)
 aggs=[dict(system_code=r[0],profile_code=r[1],level=r[2],code=r[3].read())for r in q]
 ctx=dict(tag=tag,article=progress["article"],lot=progress["lot"],warehouse=progress["warehouse"],target_warehouse=target,source_load=source_load,plan_operation_id="IW310.PLAN:"+tag,source_trip=progress["trip"],target_trip=target_trip,inbound=inbound,outbound="QO310"+tag,barcode=progress["barcode"],source_quantity="3",units=progress["units"],aggregations=aggs,manifest_operation_id="IW310.MANIFEST:"+tag)
 Path("tmp/context310.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("Source310 retained exact departed3/registered nested sender composition4nodes/scans2/units3/codes6; no repeat birth")
p=Path("scripts/source310_marked_case.py");p.write_text(p.read_text(encoding="utf-8").replace('version=x["profile_version"]','version=x["version"]'),encoding="utf-8")
