exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import base64,urllib.request
ctx=json.loads(Path("tmp/context671.json").read_text());plan=ctx["group_plan_operation_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'and nvl(DELETED,0)=0");user,password=q.fetchone()
 for source in(ctx["first"],ctx["second"]):
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=source["lot"],cell=ctx["group_receive_cell"]);assert q.fetchone()==(3,0)
  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=source["lot"]);assert q.fetchone()[0]==3
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)like '%DIRECT_UNIT.CURRENT_UID%' and upper(SQL_TEXT)not like '%V$SQL%' order by LAST_ACTIVE_TIME desc fetch first 2 rows only""");stats=q.fetchall()
headers={"Authorization":"Basic "+base64.b64encode((user+":"+password).encode()).decode()}
path="http://127.0.0.1:8088/api/inventory/interwarehouse/group-plans/"+urllib.parse.quote(plan,safe="")
with urllib.request.urlopen(urllib.request.Request(path,headers=headers),timeout=15)as response:detail=json.load(response)
assert len(detail["lots"])==2 and detail["receipt_operation_id"]==ctx["group_receipt_operation_id"]
modes={profile["scan_mode"]for lot in detail["lots"]for profile in lot["scan_profiles"]};assert {"BOX","PALLET","UNIT_OR_AGGREGATION"}<=modes
payload={**ctx["group_receipt_metadata"],"operation_id":ctx["group_receipt_operation_id"],"plan_operation_id":plan}
path="http://127.0.0.1:8088/api/inventory/interwarehouse/group-receive"
with urllib.request.urlopen(urllib.request.Request(path,headers={**headers,"Content-Type":"application/json"},data=json.dumps(payload).encode(),method="POST"),timeout=20)as response:replay=json.load(response)
assert replay==ctx["group_receipt"]
print(json.dumps({"status":"PASS","two_skus":2,"available_units":6,"receipt_replay_exact":True,"current_profile_modes":sorted(modes),"direct_scan_guard_stats":stats}))
