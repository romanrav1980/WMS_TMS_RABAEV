import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("""select b.OPERATION_ID,b.CLOSED_OPERATION_ID,b.OWNER_WARE_ID,x.LOAD_OPERATION_ID
 from RRL_TARE_BOOK b join RRL_TARE_OFFER_BOOK x on x.BOOK_OPERATION_ID=b.OPERATION_ID
 where b.STATUS='TRANSFERRED' and b.OPERATION_ID like 'TARE.CARGO.BOOK:%'
 order by b.CLOSED_AT desc fetch first 1 row only""")
 book,accepted,ware,loadop=q.fetchone()
 q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=1",ware=ware)
 assert dict(q.fetchall())=={"WAREHOUSE":0,"VEHICLE":1}
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=accepted);assert q.fetchone()==(0,)
 q.execute("select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=accepted);assert q.fetchone()==("APPLIED",)
 q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=loadop);assert q.fetchone()[0] in ("LOADED","DEPARTED")
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL
 where upper(SQL_TEXT) like '%RRL_TARE_OFFER_BOOK%' and upper(SQL_TEXT) not like '%V$SQL%'
 and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 4 rows only""")
 print("PASS102 retained exact original booking/load/accept, ware0 vehicle1 goods-event0 APPLIED")
 print("Slow SQL milliseconds/executions:",q.fetchall())
