"""Read-only rules on retained vehicle and SAP preparation; no new fixture or stock."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=10000;q=c.cursor();q.execute("set transaction read only")
 names=("RRL_VEHICLE_PROFILE_API","RRL_TRANSPORT_PLAN_RULES","RRL_TRANSPORT_PLAN_API","RRL_STOCK_LOAD_THERMAL")
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in(:n0,:n1,:n2,:n3)",dict(zip(("n0","n1","n2","n3"),names)))
 assert q.fetchall()==[]
 cases=[("mixed",[{"pallet_type_id":1,"places":8},{"pallet_type_id":3,"places":4}],0,"COMPATIBLE"),
        ("trolleys",[{"pallet_type_id":3,"places":20}],0,"COMPATIBLE"),
        ("over",[{"pallet_type_id":1,"places":9},{"pallet_type_id":3,"places":1}],0,"INCOMPATIBLE"),
        ("no_cross_variant_sum",[{"pallet_type_id":1,"places":1},{"pallet_type_id":3,"places":5}],0,"INCOMPATIBLE"),
        ("unsupported",[{"pallet_type_id":2,"places":1}],0,"INCOMPATIBLE"),
        ("unknown",[],1,"TARE_TYPE_UNCONFIRMED")]
 for code,counts,unknown,status in cases:
  value=read_oracle_json(q.callfunc("RRL_VEHICLE_PROFILE_API.check_floor_capacity",oracledb.DB_TYPE_CLOB,[10100,json.dumps(counts),unknown]))
  assert value["status"]==status,(code,value);result[code]=value
 source=json.loads(Path("tmp/context1118.json").read_text(encoding="utf-8"))
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle",[10100,json.dumps(["SAP_2135"]),0,out])
 preview=read_oracle_json(out.getvalue())
 assert preview["floor_capacity"]["status"]=="TARE_TYPE_UNCONFIRMED" and preview["floor_capacity"]["unconfirmed_places"]==2,preview
 try:q.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle",[10100,json.dumps(["SAP_2135"]),1,out]);raise AssertionError("Unknown type admitted")
 except oracledb.DatabaseError as exc:assert "PLAN_TARE_CURRENT_PLACE_TYPE_REQUIRED"in str(exc),str(exc)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399")
 stock=list(q.fetchone());assert stock==[20,20]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like 'select /* PLAN_TARE_BOUND1186 */%' and EXECUTIONS>0""")
 slow=[list(x)for x in q]
evidence={"state":"DONE","cases":result,"preview":preview,"unknown_final_refused":True,"protected_stock":stock,"slow_sql":slow,"scope":"read-only shared rule; no physical TOP acceptance"}
Path("tmp/read1187_vehicle_floor_rule.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps({"case":"PASS1187","cases":list(result),"unconfirmed_places":2,"stock":stock,"slow_sql":slow}))
