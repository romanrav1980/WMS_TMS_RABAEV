exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for sql in ["select SEQUENCE_NAME from USER_SEQUENCES where SEQUENCE_NAME like '%PALLET_TYPE%'","select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_PALLET_TYPE'order by COLUMN_ID","select WARE_ID,PALLET_TYPE_ID,CELL_CODE,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1112"]:
  q.execute(sql);print(json.dumps(q.fetchall(),default=str))
