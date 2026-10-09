"""Fail closed on direct private legacy helpers after cutover."""
import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving.py")
s=p.read_text(encoding="utf-8")
needle="        # Existing enabled event trigger is the sole writer of RRL_REMAINS."
assert s.count(needle)==1
s=s.replace(needle,"""        # Only dormant legacy receipt reaches this helper. ACTIVE uses receipt_commands.
        cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        release = cur.fetchone()
        if not release or release[0] != "PREPARED":
            raise RuntimeError("RECEIPT_POSTING_REQUIRED")""",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/services/picking_service.py")
s=p.read_text(encoding="utf-8")
needle="    def _apply_case_pick_stock_fact(self, task: dict[str, Any], fact_qty: float) -> None:\n"
assert s.count(needle)==1
s=s.replace(needle,needle+"""        release = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if not release or release[0]["state"] != "PREPARED":
            raise HTTPException(409, detail={"code": "CASE_PICK_CONFIRM_REQUIRED"})
""",1)
out[str(p)]=s
p=Path("scripts/stock_posting_install.py")
s=p.read_text(encoding="utf-8")
duplicate='"ARTICULS", "ARTICULS_SP_OLD", "RRL_CLEAR_OTBOR_CELL", "ARTICULS", "ARTICULS_SP_OLD", "RRL_CLEAR_OTBOR_CELL",'
s=s.replace(duplicate,'"ARTICULS", "ARTICULS_SP_OLD", "RRL_CLEAR_OTBOR_CELL",',1)
needle='                    "RRL_STOCK_COMPAT_FLAG_GUARD",'
assert s.count(needle)==1
names=["REMAINS"]
for n in ["RRL_SET_SCAN_PROOVE","RRL_SET_SCAN_PROOVE2","RRL_TRIAL_BY_WEIGHT","RRL_TRIAL_BY_WEIGHT2","RRL_UPDATE_PALLET_ROW2","RRL_UPDATE_PALLET_ROW3"]:
 names += [n,n+"_SP_OLD"]
 if "UPDATE_PALLET" in n:names.append(n+"_SP_CALC")
s=s.replace(needle,"                    "+", ".join('"'+n+'"' for n in names)+",\n"+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
