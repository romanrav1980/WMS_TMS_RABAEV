exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/progress383.json").read_text());op=ctx["body"]["operation_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATE,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);state,result=q.fetchone();result=read_oracle_json(result);print(json.dumps({"state":state,"status":result.get("status"),"weight":result.get("weight"),"accepted_lines":result.get("accepted_lines")},default=str));ctx["result"]=result;Path("tmp/context383.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
