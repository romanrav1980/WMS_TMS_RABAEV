exec(open("scripts/inspect226.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from pathlib import Path
import json,re
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE='PACKAGE BODY'and OBJECT_NAME not like 'BIN$%'order by OBJECT_NAME");names=[x[0]for x in q.fetchall()]
 assert all(re.fullmatch("[A-Z0-9_]+",x)for x in names)
 print(json.dumps({"db/migrations/2026-10-11_ni062_marked_receiving/004_recompile.sql":"".join("alter package "+x+" compile body;\n/\n"for x in names)}))
