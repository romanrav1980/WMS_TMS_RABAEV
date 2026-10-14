exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context376.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=ctx["load_operation_id"]);value=q.fetchone()[0];archive=json.dumps(value)if isinstance(value,dict)else value.read()if hasattr(value,"read")else value
 q.setinputsizes(archive=oracledb.DB_TYPE_CLOB)
 sql="""select count(*),min(trunc(cast(t.STARTED_AT_INSTANT at time zone(:zone)as timestamp)))
 from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID and t.WARE_ID=:ware and t.STARTED_AT_INSTANT is not null
 join json_table(:archive,'$.nodes[*]'columns(UID_VALUE varchar2(160)path '$.uid',KIND_VALUE varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))j
 on j.UID_VALUE=b.BOX_UID and j.KIND_VALUE='CASE'and j.CASE_ID=t.CASE_PICK_TASK_ID where b.LOAD_OPERATION_ID=:op"""
 try:q.execute(sql,zone="Pacific/Kiritimati",ware=ctx["warehouse"],archive=archive,op=ctx["load_operation_id"]);print(q.fetchall())
 except oracledb.DatabaseError as e:print(e)
