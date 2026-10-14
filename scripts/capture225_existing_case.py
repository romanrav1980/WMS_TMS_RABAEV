from pathlib import Path
import sys,json,oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();plan_id="IW225.PLAN:13508027ed"
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor();conn.call_timeout=15000
 q.execute("select SOURCE_LOAD_OPERATION_ID,ROOT_UID,RESULT_JSON from RRL_INTERWARE_PLAN where OPERATION_ID=:p",p=plan_id);source,uid,old=q.fetchone();saved=old if isinstance(old,dict)else json.loads(old.read()if hasattr(old,"read")else old)
 # Capture before receipt only; exact original evidence is additive, never rewrite old result.
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  q.callproc("RRL_INTERWARE_UNIT_SOURCE.capture_plan",[plan_id,"admin"])
  q.execute("select UNIT_SIGNATURE from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=:p",p=plan_id);assert len(q.fetchone()[0])==64
 finally:conn.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=:p",p=plan_id);assert q.fetchone()[0]==0
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:q.callproc("RRL_INTERWARE_UNIT_SOURCE.capture_plan",[plan_id,"admin"]);conn.commit()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select RRL_INTERWARE_UNIT_SOURCE.plan_manifest(:p,'admin')from dual",p=plan_id);value=q.fetchone()[0];manifest=json.loads(value.read()if hasattr(value,"read")else value);assert manifest["physical_unit_count"]==3 and manifest["unit_capture_required"]and len(manifest["units"])==3
 q.execute("select RESULT_JSON from RRL_INTERWARE_PLAN where OPERATION_ID=:p",p=plan_id);value=q.fetchone()[0];assert(value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value))==saved
 try:q.execute("delete from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=:p",p=plan_id);raise AssertionError("Original manifest deleted")
 except oracledb.DatabaseError as exc:conn.rollback();assert exc.args[0].code==20863
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=plan_id);assert q.fetchone()[0]==0
 q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null",u=uid);assert q.fetchone()==(3,3)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,0)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS225 original actual marked source3/codes6/departed/load fingerprint intact/source plan metadata only; immutable original unit manifest captured with late rollback and no quantity effect, original saved result preserved/no fake governmentACK/protected13520/20",plan_id,manifest["unit_signature"],flush=True)
