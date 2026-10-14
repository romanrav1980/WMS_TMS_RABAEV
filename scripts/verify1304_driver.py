exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 out={}
 for name,sql in {
 "errors":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_TT_OPERATION_PLAN_API'",
 "objects":"select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_TT_OPERATION_PLAN_API'",
 "binding":"select DRIVER_ID,USER_ID,ACTIVE,BINDING_VERSION from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=10018",
 "constraints":"select c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE,cc.COLUMN_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME='RRL_TRANSPORT_DRIVER_USER'",
 "trip":"select ID,VODITEL_ID,SHIPMENT_DATE from RRL_TRANSPORT_TASK where ID=33571",
 "ops":"select ID,OPERATION_CODE,FACT_START,FACT_END from RRL_TT_OPERATIONS where TT_ID=33571"
 }.items():
  q.execute(sql);out[name]=q.fetchall()
 print(json.dumps(out,default=str))
 Path("tmp/verify1304.json").write_text(json.dumps(out,default=str,indent=2),encoding="utf-8")
