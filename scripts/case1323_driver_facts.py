exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor()
 try:
  q.execute("select SEQ_TT_OPERATIONS.nextval from dual");op=q.fetchone()[0]
  q.execute("insert into RRL_TT_OPERATIONS(ID,TT_ID,OPERATION_CODE,ORD,DURATION_MIN,PLAN_START,PLAN_END)values(:op,33571,'UNLOAD',1,0,sysdate,sysdate)",op=op)
  def mark(action):
   out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TT_OPERATION_PLAN_API.mark_driver_fact",[op,10018,"OWN1306_DRIVER",action,out]);v=out.getvalue();return v if isinstance(v,dict)else json.loads(v.read()if hasattr(v,"read")else v)
  try:mark("DONE");raise AssertionError("DONE without START accepted")
  except oracledb.DatabaseError as e:assert "DRIVER_FACT_START_REQUIRED"in str(e)
  first=mark("START");repeat=mark("START");assert first["changed"]is True and repeat["changed"]is False and first["fact_start"]==repeat["fact_start"]
  done=mark("DONE");again=mark("DONE");assert done["changed"]is True and again["changed"]is False and done["fact_end"]==again["fact_end"]
  result={"first":first,"repeat":repeat,"done":done,"again":again,"fixture":"rollback only; no committed driver fact"}
 finally:c.rollback()
 q.execute("select count(*)from RRL_TT_OPERATIONS where ID=:op",op=op);assert q.fetchone()[0]==0
Path("tmp/result1323.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))
