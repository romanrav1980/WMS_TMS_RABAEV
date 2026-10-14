from pathlib import Path
import json
root="db/migrations/2026-10-11_ni011_exact_source/"
p=Path("db/migrations/2026-10-11_sap_gateway_actor/001_scope.sql");original=p.read_text(encoding="utf-8")
updated=original.replace("'sap_store_decision_import')","'sap_store_decision_import','sap_supply_import')").replace("not in('sap_store_order_import','customer_order_import')","not in('sap_store_order_import','customer_order_import','sap_supply_import')")
out={root+"000_scope_before.sql":original,root+"001_scope.sql":updated,root+"apply.sql":"@001_scope.sql\n",root+"rollback.sql":"@000_scope_before.sql\n"}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8");s+="\nfrom .infrastructure.sap_quantity import convert_sap_source_quantity\n";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py");s=p.read_text(encoding="utf-8")
start=s.index("            factors = ");end=s.index("            weight = ",start)
s=s[:start]+"""            from ...inventory.public import convert_sap_source_quantity
            qty = convert_sap_source_quantity(cur,line["material"],line["unit"],line["quantity"],base,read_oracle_json(units))
"""+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .supply_amendments import SupplyAmendments","from .supply_amendments import SupplyAmendments\nfrom .supply_scope import supply_transaction,assert_supply_scope")
s=s.replace('with self.gateway.transaction("NI01 SAP warehouse supply order") as cur:','with supply_transaction(self.gateway,actor,order["warehouse_id"]) as cur:')
s=s.replace('lock table RRL_SAP_SUPPLY_ORDER in share row exclusive mode','lock table RRL_SAP_SUPPLY_ORDER in share row exclusive mode wait 3')
s=s.replace('            cur.execute("select PAYLOAD_HASH,RESULT_JSON','            assert_supply_scope(cur,actor,order["warehouse_id"])\n            cur.execute("select PAYLOAD_HASH,RESULT_JSON',1)
start=s.index("            ratios = ");end=s.index("            SupplyAmendments",start)
s=s[:start]+"""            from ...inventory.public import convert_sap_source_quantity
            quantity = convert_sap_source_quantity(cur,line["material"],line["unit"],line["quantity"],master[0],units)
"""+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/api/supply_routes.py");s=p.read_text(encoding="utf-8")
# Existing API catches read PermissionError elsewhere; add import-path catch before input error.
marker="    except (ValueError,"
if marker in s:
 s=s.replace(marker,"    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n"+marker,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
