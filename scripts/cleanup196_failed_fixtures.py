import sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.weighted_planning import WeightedPlanning
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for tag,revision in[("5a59c3e883",273),("3050aa6b4f",274),("acbb6a8b40",275),("39bd805494",276)]:
  article="QW196"+tag.upper();ware=20000000+int(tag[:6],16)
  q.execute("select CHOICE_ID from RRL_PICK_WEIGHT_CHOICE where ARTICLE=:p_article and STATUS in('ACCEPTED','USED')",p_article=article)
  for(choice,)in q.fetchall():WeightedPlanning(OracleGateway()).cancel(choice,"Retire own196 failed software fixture after native cancellation","admin")
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:p_article and REMAIN>0",p_article=article)
  rows=q.fetchall();counts=[]
  for uid,cell,unit,version,hard in rows:
   assert hard==0,(uid,hard)
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell)
   counts.append({"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[x[0]for x in q.fetchall()]})
  if counts:StockPosting().post(StockCommand(operation_id="QA196.CLEAN:"+uuid4().hex,command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":revision},metadata={"reason":"Retire own196 failed fixture after metadata transport recovery","counts":counts},lines=()))
  q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor="QA196"+tag);c.commit()
  q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:p_article",p_article=article);assert q.fetchone()==(0,0)
  print("Retired owned196",tag,"P/H0 choicehistory retained actor retired",flush=True)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
