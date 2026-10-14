exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select OPERATION_ID,RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where COMMAND_TYPE='HU_SHIP'and STATE='APPLIED'order by CREATED_AT desc fetch first 1 rows only")
 op,wire=q.fetchone();d=read_oracle_json(wire)['domain']
 print(op,list(d))
 for part in d['shipments']: print(json.dumps(part['domain'],ensure_ascii=True)[:2600])
