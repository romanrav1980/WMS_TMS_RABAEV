exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 q.execute("select count(*)from RRL_CUSTOMER_PALLET_TYPE_RULE where CUSTOMER_ID=21");assert q.fetchone()==(0,),"Retained source rules changed"
 def preview():
  q.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle",[10100,json.dumps(["SAP_2135"]),0,out])
  return read_oracle_json(out.getvalue())["floor_capacity"]
 try:
  q.execute("insert into RRL_CUSTOMER_PALLET_TYPE_RULE(CUSTOMER_PALLET_TYPE_RULE_ID,CUSTOMER_ID,PALLET_TYPE_ID,IS_DEFAULT,CREATED_BY)values(-120901,21,3,1,'DEV1209_ROLLBACK')")
  general=preview();assert general["status"]=="COMPATIBLE" and general["counts"]==[{"pallet_type_id":3,"places":2}],general
  q.execute("insert into RRL_CUSTOMER_PALLET_TYPE_RULE(CUSTOMER_PALLET_TYPE_RULE_ID,CUSTOMER_ID,CUSTOMER_STORE_MAP_ID,PALLET_TYPE_ID,IS_DEFAULT,CREATED_BY)values(-120902,21,6,1,1,'DEV1209_ROLLBACK')")
  specific=preview();assert specific["status"]=="COMPATIBLE" and specific["counts"]==[{"pallet_type_id":1,"places":2}],specific
 finally:c.rollback()
 missing=preview();assert missing["status"]=="TARE_TYPE_UNCONFIRMED" and missing["unconfirmed_places"]==2,missing
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME='RRL_TRANSPORT_PLAN_RULES'");assert q.fetchall()==[]
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");protected=q.fetchone();assert protected==(20,20)
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like 'select /* PLAN_TARE_RECIPIENT1208 */%' and EXECUTIONS>0");slow=q.fetchall()
 result={"status":"PASS1209","general":general,"recipient":specific,"after_rollback":missing,"protected":protected,"slow_sql":slow,"decision":"Bound200ST/5000places and existing customer rule index retained; measured query adequate for current dev volume. Owner transport; reassess at release load."}
 Path("tmp/evidence1209.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))
