exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
p=json.loads(Path("tmp/source328_progress.json").read_text(encoding="utf-8"));tag=p["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TARGET_WARE_ID,TARGET_TT_ID,INBOUND_DOCK,OUTBOUND_DOCK,SOURCE_LOAD_OPERATION_ID,SOURCE_TT_ID from RRL_INTERWARE_PLAN where OPERATION_ID=:plan_id",plan_id="IW328.PLAN:"+tag)
 target,target_trip,inbound,outbound,load,trip=q.fetchone()
 q.execute("select STATUS,ROOT_UID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",load_id=load);assert q.fetchone()==("DEPARTED",p["lot"])
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id",lot_id=p["lot"]);assert q.fetchone()==(0,)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=p["lot"]);assert q.fetchone()==(0,0)
 context={"tag":tag,"article":p["article"],"lot":p["lot"],"warehouse":p["warehouse"],"target_warehouse":target,"source_load":load,"plan_operation_id":"IW328.PLAN:"+tag,"source_trip":trip,"target_trip":target_trip,"inbound":inbound,"outbound":outbound,"barcode":p["barcode"],"source_quantity":"3"}
 Path("tmp/context328.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
 print("SOURCE328 finalized same alreadycreatedsource/plan/ordinary3/issuedP0,no registryunits; no recreation")
