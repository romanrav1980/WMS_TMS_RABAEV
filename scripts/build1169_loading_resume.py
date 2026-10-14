from pathlib import Path
import json
s=Path("scripts/case1168_loading_temperature.py").read_text(encoding="utf-8")
defs=s[s.index(" def meta("):s.index(' q.execute("select user,')]
tail=s[s.index(' meta("insert into RRL_RECEIPT_SKU_RULE'):]
tail=tail.replace("RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,TEMP_MIN,TEMP_MAX)values(:ware,:a,2,6)","RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:ware,:a,:cell,2,6)").replace('a=article)\n from app.modules.transport.infrastructure.vehicle_profile','a=article,cell=dst)\n from app.modules.transport.infrastructure.vehicle_profile',1)
head="""exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
from app.oracle_gateway import OracleGateway
context_path=Path("tmp/context1168.json");context=json.loads(context_path.read_text(encoding="utf-8"))
assert context["state"]=="BUILDING","This continuation starts after pick/bind/move; do not replay after loading"
tag=context["tag"];lot=context["lot"];ware=context["warehouse_id"];shipcell=context["ship_cell"];dst=context["target_cell"]
st_uid=context["st_identifier"];article=context["article"];vehicle=context["vehicle_id"];trip=context["trip_id"];dock=context["dock"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as conn:
 conn.call_timeout=15000;q=conn.cursor()
"""
head+=defs
head+=""" q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SKU_RULE'and NULLABLE='N'order by COLUMN_ID");print("Required SKU columns",json.dumps(q.fetchall()),flush=True)
"""
print(json.dumps({"scripts/resume1169_loading_temperature.py":head+tail}))
