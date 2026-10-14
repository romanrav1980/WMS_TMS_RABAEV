exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_HAS_WRIGHT'order by LINE");source="".join(row[0]for row in q.fetchall());print("LEGACY_HAS_ACTIVE_CHECK", "DELETED"in source.upper())
 q.execute("select count(*)from RUSERS where USER_GROUP='SAP_GATEWAY'and ID!='SAP_FILE_GATEWAY'");print("OTHER_GATEWAY_MEMBERS",q.fetchone()[0])
