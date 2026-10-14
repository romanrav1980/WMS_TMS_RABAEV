import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.oracle_gateway import OracleGateway
print(json.dumps(OutgoingQuality(OracleGateway()).status("FULL.ST:562cdaa306","admin"),ensure_ascii=True))
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u="FULL.QA:562cdaa306");print("BARCODE",q.fetchall())
 q.execute("select text from user_source where name='RRL_STOCK_QC_ITEM_SCAN' and type='PACKAGE BODY' order by line");print("".join(x[0]for x in q.fetchall()))
