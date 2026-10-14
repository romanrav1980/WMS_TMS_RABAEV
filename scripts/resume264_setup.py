from pathlib import Path
source=Path("scripts/case264_calendar.py").read_text(encoding="utf-8")
source=source.replace(' q.execute("select RRL_CUSTOMER_STORE_MAP_SQ.nextval from dual");map_id=int(q.fetchone()[0]);store="QCAL264"+tag',""" q.execute("select CUSTOMER_STORE_MAP_ID,STORE_CODE from RRL_CUSTOMER_STORE_MAP where CREATED_BY='QA264'and STORE_CODE like 'QCAL264%'")
 existing=q.fetchall();assert len(existing)==1;map_id,store=existing[0];tag=store[7:];actor="CAL264"+tag;group=actor.upper()[:15]""")
source="\n".join(line for line in source.split("\n")if not line.startswith(' meta("insert into RRL_CUSTOMER_STORE_MAP'))
exec(compile(source,"resume264_setup.py","exec"))
