import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway();out={}
for ware,article in[(6667491,"QNATIVED9A5C53B54"),(20052672,"QC16700CDC0EF51")]:
 rows=g.fetch_all("select RRL_STOCK_POOL_READ.snapshot_json(:p_ware,:p_article)SNAPSHOT from dual",{"p_ware":ware,"p_article":article})
 out[f"{ware}:{article}"]=json.loads(rows[0]["snapshot"])
print(json.dumps({"tmp/ni033_pool_before171.json":json.dumps(out,ensure_ascii=False,indent=2)}))
