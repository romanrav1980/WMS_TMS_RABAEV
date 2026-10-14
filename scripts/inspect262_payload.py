exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where COMMAND_TYPE='SAP_RECEIPT'and STATE='APPLIED'and ACTOR='admin'order by APPLIED_AT desc fetch first 1 rows only");row=q.fetchone()
 assert row,"No existing actual receipt"
 body=json.loads(row[0].read());print("METADATA_KEYS",list(body["metadata"]));print("SOURCE_KEYS",list(body["source"]))
 Path("tmp/replay262_source.json").write_text(json.dumps(body,ensure_ascii=True),encoding="utf-8")
