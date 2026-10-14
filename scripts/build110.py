from pathlib import Path
import json
f=Path("db/migrations/2026-10-10_ni062_disposal");out={}
p=Path("db/migrations/2026-10-08_stock_posting_core")
s=(p/"427_before110_effect.sql").read_text(encoding="utf-8-sig")
s=s.replace("package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE)","package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_CORRECTION_CORE,package RRL_STOCK_RETURN_DISPOSE)")
s=s.replace("p_supplier_return_receipt varchar2 default null)","p_supplier_return_receipt varchar2 default null,p_disposal_receipt varchar2 default null)")
old="if p_supplier_return_receipt is null then RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');"
new="if p_supplier_return_receipt is not null and p_disposal_receipt is not null then raise_application_error(-20886,'CONSUMPTION_ONE_EXPLICIT_EXCEPTION_REQUIRED');end if;\n  if p_disposal_receipt is not null then RRL_STOCK_RETURN_DISPOSE.validate_consume(p_disposal_receipt,p_uid,p_cell,p_qty,p_warehouse,p_actor);RRL_STOCK_LOCATION_CORE.assert_quarantine(p_cell,p_warehouse);\n  elsif p_supplier_return_receipt is null then RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');"
assert old in s;s=s.replace(old,new);out[str(f/"003_effect.sql")]=s
s=(p/"426_before110_root.sql").read_text(encoding="utf-8-sig")
for old,new in [
 ("elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.compile_command","elsif g_kind='STORE_RETURN_DISPOSE' then RRL_STOCK_RETURN_DISPOSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.compile_command"),
 ("elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.execute_command","elsif g_kind='STORE_RETURN_DISPOSE' then RRL_STOCK_RETURN_DISPOSE.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.execute_command")]:
 assert old in s;s=s.replace(old,new)
out[str(f/"004_root.sql")]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8-sig");s=s.replace('{"TARE_LOSS_REPORT"', '{"STORE_RETURN_DISPOSE", "TARE_LOSS_REPORT"');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
