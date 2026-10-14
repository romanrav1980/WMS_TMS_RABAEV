"""157 own published metadata/no stock; immutable proposal save/replay/cancel/current scope."""
import sys,json
from pathlib import Path
from datetime import date
from decimal import Decimal
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import build_slotting_demand,build_range_proposal
from app.modules.inventory.contracts_range_proposal import RangeDraft
from app.modules.inventory.contracts_slotting import SlottingError
s=get_settings();tag='52470cc7';ware=6667491;article="QNATIVED9A5C53B54"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);stock=q.fetchone()
 route=146;faces=[518,519]
 q.execute("select PICK_FACE_ID from RRL_PICK_FACE where WARE_ID=:ware and PICK_ROUTE_ID=:route and ACTIVE=1 order by PICK_FACE_ID",ware=ware,route=route)
 assert [row[0]for row in q.fetchall()]==faces
 costs=[{"pick_face_id":faces[0],"pick_seconds_per_base":"1","replenish_seconds_per_pallet":"60","basis":"Own explicit route assumption"},
        {"pick_face_id":faces[1],"pick_seconds_per_base":"0.5","replenish_seconds_per_pallet":"150","basis":"Own explicit route assumption"}]
 reader=build_slotting_demand(OracleGateway());service=build_range_proposal(OracleGateway())
 preview=reader.preview(ware,article,date(2026,10,10),date(2026,10,11),Decimal(1),"EA","admin",Decimal(2),costs)
 assert preview["range_recommendation"]["status"]=="NOMINAL_RECOMMENDATION",preview["range_recommendation"]
 op="RANGE157.SAVE2:"+tag
 command=RangeDraft(op,date(2026,10,10),date(2026,10,11),Decimal(1),"EA",Decimal(2),costs,preview["source_signature"],"Own explicit draft only")
 with ThreadPoolExecutor(max_workers=2)as pool:
  results=list(pool.map(lambda _:service.save(ware,article,command,"admin"),range(2)))
 assert results[0]==results[1] and results[0]["status"]=="DRAFT",results
 assert service.get(ware,article,op,"admin")["source"]["range_recommendation"]["selected_faces"][0]["pick_face_id"]==faces[0]
 def denied(fn,code):
  try:fn()
  except SlottingError as exc:assert code in str(exc) or code==exc.code,(exc.code,str(exc))
  else:raise AssertionError("Expected refusal")
 bad=RangeDraft(**{**command.__dict__,"reason":"Different request content"})
 denied(lambda:service.save(ware,article,bad,"admin"),"PICK_RANGE_OPERATION_CONTENT_CONFLICT")
 denied(lambda:service.save(ware,article,command,"UNKNOWN157"),"PICK_RANGE_CURRENT_WARE_ACTOR_REQUIRED")
 cancelled=service.cancel(ware,article,op,"RANGE157.CANCEL2:"+tag,"Cancel only own review proposal","admin")
 assert cancelled["status"]=="CANCELLED"
 assert service.cancel(ware,article,op,"RANGE157.CANCEL2:"+tag,"Cancel only own review proposal","admin")==cancelled
 assert service.save(ware,article,command,"admin")==results[0]
 current=service.get(ware,article,op,"admin");assert current["status"]=="CANCELLED" and current["created_by"]=="admin"
 # Retain one explicit draft for approval/drain continuation; no range applied.
 active=RangeDraft(**{**command.__dict__,"operation_id":"RANGE157.ACTIVE2:"+tag,"reason":"Own draft retained for range approval continuation"})
 assert service.save(ware,article,active,"admin")["status"]=="DRAFT"
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);assert q.fetchone()==stock==(20,20)
 q.execute("select count(*)from RRL_PICK_FACE_ARTICUL where PICK_FACE_ID in(:a,:b)",a=faces[0],b=faces[1]);assert q.fetchone()==(0,)
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.get(f"http://127.0.0.1:8088/api/inventory/slotting/warehouses/{ware}/articles/{article}/recommendations/"+active.operation_id)
  assert r.status_code==200,(r.status_code,r.text[:1000]);assert r.json()["status"]=="DRAFT"
 print("PASS157 two workers one immutable draft/exact replay-after-cancel/changed request conflict/current actor/source archive/cancel/history/no assignment/P20H20; retained",active.operation_id,"faces",faces,"route",route,flush=True)
