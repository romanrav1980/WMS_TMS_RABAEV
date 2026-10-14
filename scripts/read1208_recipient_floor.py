exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME='RRL_TRANSPORT_PLAN_RULES'");errors=q.fetchall();assert not errors,errors
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_TRANSPORT_PLAN_RULES.check_vehicle",[10100,json.dumps(["SAP_2135"]),0,out]);preview=read_oracle_json(out.getvalue())
 q.execute("select CUSTOMER_ID,CUSTOMER_STORE_MAP_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=2135");customer=q.fetchone()
 q.execute("select CUSTOMER_PALLET_TYPE_RULE_ID,CUSTOMER_STORE_MAP_ID,PALLET_TYPE_ID,IS_DEFAULT from RRL_CUSTOMER_PALLET_TYPE_RULE where CUSTOMER_ID=:customer and ACTIVE=1 and trunc(sysdate)between VALID_FROM and nvl(VALID_TO,date '2999-12-31')",customer=customer[0]);rules=q.fetchall()
 loaded={}
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like 'select /* PLAN_TARE_RECIPIENT1208 */%' and EXECUTIONS>0");slow=q.fetchall()
 result={"native_errors":errors,"source_customer":customer,"existing_rules":rules,"prepared_floor":preview.get("floor_capacity"),"loaded_floor":loaded.get("floor_capacity"),"slow_sql":slow}
 Path("tmp/evidence1208.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))
