from pathlib import Path
import json
root=Path("db/migrations/2026-10-11_sap_gateway_actor")
p=Path("db/migrations/2026-10-11_ni022_source_scope/001_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("'customer_order_view','sap_store_order_import','customer_order_import'","'customer_order_view','sap_store_order_import','customer_order_import','sap_store_order_decision_import'")
s=s.replace("case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'then 1 else 0 end into","case when upper(trim(USER_GROUP))='GLOBAL_ADMIN'\n    or(p_permission in('sap_store_order_import','sap_store_order_decision_import')and RRL_HAS_WRIGHT(ID,'sap_store_order_import_all_ware')=1)then 1 else 0 end into")
# Permission fence is stateless; body-only live change preserves parsed call signatures.
out={str(root/"001_scope.sql"):s,str(root/"001b_scope_body.sql"):s[s.lower().index("create or replace package body"):]}
print(json.dumps(out,ensure_ascii=True))
