from pathlib import Path
import ast,json
s=Path("scripts/source291_ordinary_case.py").read_text(encoding="utf-8");tree=ast.parse(s)
withnode=next(n for n in tree.body if isinstance(n,ast.With))
defs="\n\n".join(ast.unparse(n)for n in withnode.body if isinstance(n,ast.FunctionDef))
start=s.index("        born = api(");end=s.index("    finally:",start)
tail=s[start:end];tail="\n".join(line[4:]if line.startswith("    ")else line for line in tail.splitlines())+"\n"
prefix='''exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx
progress=json.loads(Path("tmp/source291_progress.json").read_text(encoding="utf-8"))
globals().update(progress);ware=progress["warehouse"];gtin=progress["barcode"];units=[]
cfg=s;admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor()
 q.execute("select p.PICK_TASK_ID,p.PICK_PLAN_ID,p.PICK_PLAN_LINE_ID,p.CUSTOMER_ID from RRL_WAREHOUSE_TASK t join RRL_PICK_WAVE_TASK w on w.PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID join RRL_PICK_TASK p on p.PICK_TASK_ID=w.PICK_TASK_ID where t.TASK_ID=:task_id",task_id=task)
 pt,plan,pl,customer=q.fetchone()
 q.execute("select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:order_id",order_id=order);ff=q.fetchone()[0]
 q.execute("select TRANSTYPE,VODITEL_ID from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=trip);trtype,driver=q.fetchone()
 q.execute("select count(*)from RRL_PALLETS where UID_PALLET=:lot_id",lot_id=lot)
 assert q.fetchone()==(0,),"Birth already performed; resume later stage without recreating"
 conn.rollback()
'''
prefix+="\n".join(" "+line if line else ""for line in defs.splitlines())+"\n"
# Definitions inside the old with use four-space indentation after unparse.
# Standardize all resume statements to one consistent leading indentation.
prefix=prefix.replace('\n q','\n    q').replace('\n pt,','\n    pt,').replace('\n assert ','\n    assert ').replace('\n conn.rollback()','\n    conn.rollback()')
defsind="\n".join("    "+line if line else ""for line in defs.splitlines())+"\n"
prefix=prefix[:prefix.index("\n def ")]+ "\n"+defsind if "\n def "in prefix else prefix
# Simpler rebuild fixed prefix indentation from the untouched literal.
header=prefix[:prefix.index('\n    def meta')]
out=header+"\n"+defsind+tail
ast.parse(out)
print(json.dumps({"scripts/resume291_source.py":out},ensure_ascii=True))
