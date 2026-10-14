import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
g=OracleGateway();j=OutgoingQuality(g).status("MIXED172.ST:00cdc0ef51");print(json.dumps(j,ensure_ascii=True))
print(g.fetch_all("select OPERATION_ID,to_clob(RESULT_JSON)RESULT from RRL_STOCK_OPERATION where OPERATION_ID in('MIXED172.QC.SCAN','MIXED172.QC.WEIGHT')"))
