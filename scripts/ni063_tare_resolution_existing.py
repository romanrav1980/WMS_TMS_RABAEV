import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select OPERATION_ID,DAMAGE_OPERATION_ID from RRL_TARE_RESOLUTION where RESOLUTION_KIND='WRITE_OFF' and OPERATION_ID like 'TARE.WRITEOFF:%' order by CREATED_AT desc fetch first 1 row only")
 writeoff,damage=q.fetchone()
 q.execute("select OUTSTANDING_QTY,CONDITION_CODE,POLICY_VERSION from RRL_TARE_STORE_DEBT where CLAIM_KEY=:damage",damage=damage);assert q.fetchone()==(1,'DAMAGED',1)
 q.execute("select sum(QUANTITY) from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3");assert q.fetchone()==(5,)
 for op in [damage,writeoff]:
  q.execute("select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);assert q.fetchone()==('APPLIED',)
 print("PASS100 committed damage2, independent writeoff1, total tare5/store damaged debt1; original deadline policy1 and APPLIED history retained")
