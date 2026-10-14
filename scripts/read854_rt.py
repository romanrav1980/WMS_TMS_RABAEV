exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context850.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select PICK_WAVE_REPLENISH_TASK_ID,REPLENISHMENT_QTY_MODE,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,RESERVE_OPERATION_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w",w=ctx["wave"]);print(q.fetchall())
