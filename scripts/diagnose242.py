exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context242.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 body={"contract_version":2,"operation_id":"IW242.DIAG:"+ctx["tag"],"command_type":"INTERWARE_PUTAWAY_PLAN","actor":"admin","source":{"receipt_operation_id":"IW242.RECEIVE:"+ctx["tag"]},"lines":[],"units":[],"metadata":{}}
 try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(body),"admin",out,None]);print("PREPARE_OK")
 except oracledb.DatabaseError as exc:print(str(exc))
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
