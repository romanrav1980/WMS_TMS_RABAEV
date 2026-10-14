exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op='REUSE643.RECEIVE:dc1889623c');value=q.fetchone()[0];value=value.read()if hasattr(value,'read')else value;value=json.loads(value)if isinstance(value,str)else value
 Path('tmp/codex_ni062_result.json').write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value))