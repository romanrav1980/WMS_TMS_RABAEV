from pathlib import Path
import json
ctx=json.loads(Path("tmp/context292.json").read_text(encoding="utf-8"))
body=dict(ctx["receipt_metadata"]);body.pop("unit_scans");body["scans"]=ctx["units"][0]["codes"]
ctx["receipt_body"]=body
s=Path("scripts/case291_commit.py").read_text(encoding="utf-8").replace("291","292")
out={"scripts/case292_commit.py":s,"tmp/context292.json":json.dumps(ctx,indent=2)+"\n"}
s=Path("scripts/finish291_placement.py").read_text(encoding="utf-8").replace("291","292")
s=s.replace(' q.execute("select count(*)',' q.execute("select count(*)',1)
needle=' q.execute("select REMAIN,HARD_RESERVED_BASE'
assert needle in s;s=s.replace(needle,''' q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and CURRENT_CELL=:cell_code and STOCK_STATUS='AVAILABLE'",lot_id=uid,cell_code=target);assert q.fetchone()==(1,1)
 q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["lot"]);assert q.fetchone()==(2,2)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot_id",lot_id=ctx["lot"]);assert q.fetchone()==(6,)
'''+needle,1)
out["scripts/finish292_placement.py"]=s
print(json.dumps(out,ensure_ascii=True))
