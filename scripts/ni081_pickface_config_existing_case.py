"""Private135 mapping207/face508 only; failed second config stage must roll back the first."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.schemas import PickFaceArticulUpsertRequest
s=get_settings();client=httpx.Client(auth=("admin","admin123"),timeout=30)
base="http://127.0.0.1:8088/api/picking"
def post(body,status=200):
 r=client.post(base+"/pick-faces/508/articuls",json=body)
 if r.status_code==503:
  print("Unconfirmed503: repeating original natural-key configuration once",flush=True)
  r=client.post(base+"/pick-faces/508/articuls",json=body)
 assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def snapshot():
  q.execute("select json_object(* returning clob) from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=207")
  value=q.fetchone()[0];return value.read()if hasattr(value,"read")else value
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");stock=q.fetchone()
 rows=client.get(base+"/pick-faces/508/articuls")
 assert rows.status_code==200,(rows.status_code,rows.text[:1200])
 row=next(item for item in rows.json()if item["pick_face_articul_id"]==207)
 body={name:row[name]for name in PickFaceArticulUpsertRequest.model_fields if name in row}
 for key in ("valid_from","valid_to"):
  if body.get(key):body[key]=body[key][:10]
 body["pick_face_id"]=508
 before=snapshot()
 bad={**body,"priority":"777","replenishment_method":"NOT_A_METHOD"}
 post(bad,409);assert snapshot()==before,"Partial base assignment survived extended constraint failure"
 try:
  exact={**body,"priority":"100.0000000000000000001"}
  result=post(exact);assert result["pick_face_articul_id"]==207
  assert post(exact)==result
  q.execute("select to_char(PRIORITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=207")
  assert q.fetchone()[0]=="100.0000000000000000001"
  denied=post({**body,"active":0},409);assert "PICK_FACE_OLD_STOCK_REQUIRES_DRAIN"in str(denied),denied
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
  print("PASS142 private original mapping207: failed extended enum rolls back changed base priority/all original row; exact Decimal priority100.0000000000000000001/same ID repeat; occupied disable409/P20H20 unchanged",flush=True)
 finally:
  post(body)
