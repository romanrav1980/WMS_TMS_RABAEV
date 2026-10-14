import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
for wave in range(397,403):
 row=g.fetch_all("select RRL_STOCK_WAVE_FINISH_CMD.snapshot_json(:id) SNAPSHOT from dual",{"id":wave})[0]
 raw=row["snapshot"];data=raw if isinstance(raw,dict)else json.loads(raw)
 print(wave,data)
