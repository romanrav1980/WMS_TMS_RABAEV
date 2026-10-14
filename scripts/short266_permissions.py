from pathlib import Path
import json
out={}
root=Path("db/migrations/2026-10-11_sap_gateway_actor")
for p in [root/"001_scope.sql",root/"001b_scope_body.sql",root/"002_account.sql",root/"verify.sql",Path("wiki/database/retailcase_sap_gateway_actor_design_20261011.md")]:
 s=p.read_text(encoding="utf-8").replace("sap_store_order_import_all_ware","sap_store_all_ware").replace("sap_store_order_decision_import","sap_store_decision_import")
 out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
