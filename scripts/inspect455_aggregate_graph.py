exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select a.AGGREGATION_ID,a.SYSTEM_CODE,a.PROFILE_CODE,a.AGG_LEVEL,a.CODE_HASH from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID where u.UID_PALLET='100007031097593489'")
 print(q.fetchall())
 q.execute("select text from user_source where name='RRL_IW_AGG_SCAN'and type='PACKAGE BODY'and lower(text)like '%invalid%'")
 print(q.fetchall())
