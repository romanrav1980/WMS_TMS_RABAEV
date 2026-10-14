import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select STATUS from USER_OBJECTS where OBJECT_NAME='RRL_CASE_CLOSE_JOURNAL_G'");assert q.fetchone()[0]=="VALID"
 q.execute("select count(*)from USER_ERRORS where NAME='RRL_CASE_CLOSE_JOURNAL_G'");assert q.fetchone()[0]==0
 for sql in ["update RRL_CASE_PICK_EVENT set MESSAGE_TEXT='Changed'where OFFLINE_EVENT_ID='CASE.CLOSE167.DEBUG'",
             "delete from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID='CASE.CLOSE167.DEBUG'"]:
  try:q.execute(sql);raise AssertionError("Closure result history mutable")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20863,exc
  finally:c.rollback()
 print("PASS167 guardVALID/USER_ERRORSempty; original new-marker debug acknowledgment update/delete20863; no history cleanup")
