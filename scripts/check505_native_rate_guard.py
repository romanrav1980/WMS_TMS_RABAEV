exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from copy import deepcopy
ctx=json.loads(Path("tmp/context502.json").read_text(encoding="utf-8"));saved=ctx["result"];trial=deepcopy(saved)
trial["operation_id"]=saved["operation_id"]+".OLD_RATE";trial["amount"]="2.50"
trial["lines"][0].update(version=1,rate="2.5",amount="2.50")
line=trial["lines"][0]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.setinputsizes(wire=oracledb.DB_TYPE_CLOB)
 try:
  q.execute("""declare x RRL_LOGISTICS_COST_RUN%rowtype;begin select *into x from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:old_op;
  x.OPERATION_ID:=:new_op;x.PAYLOAD_HASH:=sys.dbms_crypto.hash(utl_raw.cast_to_raw(:new_op),sys.dbms_crypto.hash_sh256);
  x.RESULT_JSON:=:wire;insert into RRL_LOGISTICS_COST_RUN values x;end;""",old_op=saved["operation_id"],new_op=trial["operation_id"],wire=json.dumps(trial))
  q.execute("""insert into RRL_LOGISTICS_COST_LINE(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE,CURRENCY,RATE_KEY,VERSION_NO,QUANTITY,RATE_VALUE,AMOUNT,BASIS,RATE_DATE,PERIOD_MODE,PERIOD_TIME_ZONE,PERIOD_POLICY_VERSION)
  values(:op,:load_id,'WAREHOUSE_PICKING','GEL',:key,1,1,2.5,2.5,'BOX',to_date(:day,'YYYY-MM-DD'),:period_kind,:zone,:version)""",
            op=trial["operation_id"],load_id=line["load_operation_id"],key=line["rate_key"],day=line["rate_date"],period_kind=line["period_mode"],zone=line["period_timezone"],version=line["period_policy_version"])
 except oracledb.DatabaseError as exc:
  assert exc.args[0].code==20886 and "RATE"in str(exc),str(exc)
  print("PASS505 native stale same-date rate denied",str(exc.args[0]).split("\n")[0])
 else:raise AssertionError("Stale same-date revision admitted")
 finally:c.rollback()
 q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op=trial["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select count(*),min(AMOUNT),min(VERSION_NO)from RRL_LOGISTICS_COST_LINE where LOAD_OPERATION_ID=:op",op=line["load_operation_id"]);assert q.fetchone()==(1,3,2)
