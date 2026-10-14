exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op='STORE383.RECEIPT:c09bc5c0');value=q.fetchone()[0];value=value.read()if hasattr(value,'read')else value;data=json.loads(value)if isinstance(value,str)else value
 Path('tmp/codex_c0023_receipt_result.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data))