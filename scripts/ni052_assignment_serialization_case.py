"""Own legacy ST membership; bounded race against a locked trip, no stock fixture."""
import sys,threading
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor,TimeoutError
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts,unassign_st,cancel_trip
cfg=get_settings();tag=uuid4().hex[:10];number="ASSIGN.QA:"+tag
def connect():return oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)
with connect() as c:
 q=c.cursor()
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 a,b=seq("RRL_TRANSPORT_TASK_SQ"),seq("RRL_TRANSPORT_TASK_SQ");sid=seq("RRL_SBORKA_PALLETS_SQ")
 for tid in (a,b):q.execute("insert into RRL_TRANSPORT_TASK(ID,CONDITION,DELETED) values(:id,'Спланирован',0)",id=tid)
 q.execute("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,CONDITION) values(:id,:u,:u,0)",id=sid,u=number);c.commit()
 gateway=OracleGateway()
 try:
  assert assign_sts(gateway,a,[number])["assigned"]==1
  try:assign_sts(gateway,b,[number]);raise AssertionError("Another trip stole ST")
  except ValueError as exc:assert "another trip" in str(exc),str(exc)
  unassign_st(gateway,a,number)
  q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:id",id=sid);assert q.fetchone()==(None,)
  q.execute("select ID from RRL_TRANSPORT_TASK where ID=:id for update",id=a);q.fetchone()
  started=threading.Event()
  def contender():
   with connect() as second:
    second.call_timeout=10000;cursor=second.cursor();started.set()
    try:cursor.callfunc("RRL_TT_ADD_PALL",oracledb.DB_TYPE_VARCHAR,[a,number]);second.commit();return "incorrect success"
    except oracledb.DatabaseError as exc:second.rollback();return str(exc)
  with ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(contender);assert started.wait(2)
   try:future.result(timeout=.3);raise AssertionError("Legacy writer bypassed locked trip")
   except TimeoutError:pass
   q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID=:id",id=a);c.commit()
   outcome=future.result(timeout=12);assert "TRIP_MEMBERSHIP_CHANGE_FORBIDDEN" in outcome,outcome
  q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:id",id=sid);assert q.fetchone()==(None,)
  try:
   q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id",tt=b,id=sid);c.commit();raise AssertionError("Direct assignment bypassed writer")
  except oracledb.DatabaseError as exc:c.rollback();assert "EXPLICIT_TRIP_MEMBERSHIP_WRITER_REQUIRED" in str(exc),str(exc)
  assert assign_sts(gateway,b,[number])["assigned"]==1
  cancel_trip(gateway,b,"admin")
  q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:id",id=sid);assert q.fetchone()==(None,)
  print("PASS assign/remove reuse legacy writer; foreign trip denied; actual blocked concurrent writer rechecks trip and leaves ST unassigned",flush=True)
 finally:
  c.rollback()
  q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=null where ID=:id",id=sid)
  q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID in(:a,:b)",a=a,b=b);c.commit()
  print("Own metadata fixture unassigned/retired; no P/H or quantity journal created",flush=True)
