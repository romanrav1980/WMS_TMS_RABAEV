exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();op=json.loads(Path("tmp/356_box_candidates.json").read_text(encoding="utf-8"))[0][0]
 q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=op);tree=read_oracle_json(q.fetchone()[0]);print(json.dumps([n for n in tree["nodes"]if n["kind"]=="CASE"],ensure_ascii=True))
 q.execute("select BOX_UID,BOX_CONTENT_VERSION,CASE_BOX_TASK_ID,MEASUREMENT_ORIGIN,SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE,TARE_WEIGHT_KG,NET_WEIGHT_KG from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:op",op=op);print(json.dumps(q.fetchall()))
