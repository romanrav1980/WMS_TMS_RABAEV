from pathlib import Path
import json
old=Path("scripts/case977_wait_again.py").read_text(encoding="utf-8")
head=old[:old.index('assert not path.exists()')]
head+='record=json.loads(path.read_text(encoding="utf-8"));assert record["stage"]=="DEFERRED","Retained current phase required"\n'
head+='def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")\ng=OracleGateway();op=record["decision"]\n'
head+='with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:\n q=c.cursor()\n'
tail=old[old.index(' out=q.var(oracledb.DB_TYPE_CLOB);q.callproc'):];print(json.dumps({"scripts/continue982_case_wait.py":head+tail},ensure_ascii=True))
