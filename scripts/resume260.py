from pathlib import Path
source=Path("scripts/case260_supply_read.py").read_text(encoding="utf-8")
a=source.index(' meta("insert into RUSERS(')
b=source.index(' try:\n  own=',a)
source=source[:a]+''' q.execute("select ID,PASS,USER_GROUP from RUSERS where NAME='Own SAP receipt source reader'and ID like 'SR260%'")
 existing=q.fetchall();assert len(existing)==1
 actor,secret,group=existing[0]
 meta("update RUSERS set DELETED=0,WARE_ID=:w where ID=:a",w=ware,a=actor)
'''+source[b:]
exec(compile(source,"resume260.py","exec"))
