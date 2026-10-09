import json
from pathlib import Path
p=Path("db/migrations/2026-10-08_stock_posting_core/024_posting.sql");s=p.read_text(encoding="utf-8")
needle="  else\n   if g_kind in('MANUAL_MOVE'"
assert needle in s;s=s.replace(needle,"  else\n   begin\n   if g_kind in('MANUAL_MOVE'",1)
needle="   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;\n  end if;"
replacement="""   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;
   exception when others then
    -- A concurrent identical command may have committed while this planner read mutable stock.
    -- Rebuild only the existing replay lock plan; never take OP before the full resource plan.
    select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;
    if v_exists=0 then raise;end if;
    v_domain:=null;v_plan:=json_array_t();v_resources_json:=json_array_t();
    v_entry:=json_object_t();v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);
    v_entry:=json_object_t();v_entry.put('rank',10);v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);
    v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;
   end;
  end if;"""
assert needle in s;s=s.replace(needle,replacement,1)
out={str(p):s}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py");s=p.read_text(encoding="utf-8")
needle='''                hints, receipt_marks = plan_receipt(cursor, command_document)
                resolution = json.dumps(hints, ensure_ascii=True, separators=(",", ":"), allow_nan=False)'''
replacement='''                try:
                    hints, receipt_marks = plan_receipt(cursor, command_document)
                    resolution = json.dumps(hints, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
                except Exception:
                    # Pure preview can fail after another identical receipt has committed.
                    # Defer immutable actor/body comparison to the core replay path.
                    cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i", i=operation_id)
                    if cursor.fetchone() is None:
                        raise'''
assert needle in s;s=s.replace(needle,replacement,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/error_handlers.py");s=p.read_text(encoding="utf-8").replace('or error.oracle_code == 20872','or error.oracle_code in (20872, 20873)')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/inventory-count.js");s=p.read_text(encoding="utf-8").replace(' || [400,401,403,422].includes(error.status)','')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
