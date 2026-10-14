exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
src=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();op="HU1057.PLAN:"+src["tag"]
 q.execute("select RESULT_JSON,STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);body,state=q.fetchone();root=read_oracle_json(body);assert state=="APPLIED"
 q.execute("select RESULT_JSON from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op=op);stored=read_oracle_json(q.fetchone()[0])
 print(json.dumps({"root":root,"run":stored},ensure_ascii=True))
 Path("tmp/read1062_plan_cache.json").write_text(json.dumps({"root":root,"run":stored},indent=2),encoding="utf-8")
 # Recover the already committed phase, without manufacturing another task or stock.
 p=Path("tmp/context1057.json");ctx=json.loads(p.read_text(encoding="utf-8"))
 assert ctx["stage"]=="PACKED";ctx.update(plan=root,task=int(root["tasks"][0]["task_id"]),stage="PLANNED",plan_replay=False,phase_recovered_from_applied_root=True)
 p.write_text(json.dumps(ctx,indent=2,default=str),encoding="utf-8")
