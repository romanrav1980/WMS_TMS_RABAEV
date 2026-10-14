from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_stock_floor_type/"
p=Path(root+"003_command.sql");s=p.read_text(encoding="utf-8")
s=s.replace("PALLET_FLOOR_VERSION_CHANGED');","PALLET_FLOOR_VERSION_CHANGED');").replace("raise_application_error(-20890,'PALLET_FLOOR_VERSION_CHANGED')","raise_application_error(-20886,'PALLET_FLOOR_VERSION_CHANGED')")
s=s.replace("s clob;j json_object_t;f json_array_t:=","s clob;j json_object_t;uid_value varchar2(200);f json_array_t:=",1)
s=s.replace("s:=snapshot(p_request,d.get_string('actor'));j:=json_object_t.parse(s);","s:=snapshot(p_request,d.get_string('actor'));j:=json_object_t.parse(s);uid_value:=j.get_string('uid');",1)
s=s.replace("where UID_POLETA=j.get_string('uid')and REMAIN>0","where UID_POLETA=uid_value and REMAIN>0",1)
point="  if uid_value is null or"
insert="""  keys:=d.get_object('source').get_keys;el:=d.get_object('source').get('uid');
  if keys.count!=1 or el is null or not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_CANONICAL_SOURCE_REQUIRED');end if;
"""
s=s.replace(point,insert+point,1)
point="  version_no:=m.get_number('expected_version');"
insert="""  el:=m.get('scan_pallet');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_SCAN_TEXT_REQUIRED');end if;
  el:=m.get('scan_cell');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_SCAN_TEXT_REQUIRED');end if;
  el:=m.get('evidence_reference');if not el.is_string then raise_application_error(-20886,'PALLET_FLOOR_REFERENCE_TEXT_REQUIRED');end if;
"""
s=s.replace(point,insert+point,1);f[str(p)]=s
s=Path(root+"000_rrl_stock_posting_api_body.sql").read_text(encoding="utf-8")
point="  -- Immutable committed replay is considered"
assert point in s;s=s.replace(point,"  if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then declare doc json_object_t:=json_object_t.parse(p_request);ware_no number;begin ware_no:=RRL_PALLET_FLOOR_READ.scope_warehouse(doc.get_object('source').get_string('uid'),p_actor);end;end if;\n"+point,1)
point="   if g_kind='INTERWARE_RECOVERY_CANCEL'then RRL_STOCK_IW_RECOVERY_CANCEL.compile_command"
assert point in s;s=s.replace(point,"   if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   els"+point.lstrip(),1)
# The point begins 'if'; 'els'+'if' creates 'elsif'.
point="  if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then RRL_STOCK_MOVE_CORE.manual_whole"
assert point in s;s=s.replace(point,"  if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.execute_command(g_request,g_actor,p_result);\n  els"+point.lstrip(),1)
f[root+"004_root.sql"]=Path(root+"000_rrl_stock_posting_api_spec.sql").read_text(encoding="utf-8")+"\n"+s
s=Path(root+"000_rrl_stock_load_floor_spec.sql").read_text(encoding="utf-8")+Path(root+"000_rrl_stock_load_floor_body.sql").read_text(encoding="utf-8")
s=s.replace("root_id varchar2(200);ware_no number;","root_id varchar2(200);ware_no number;type_version number;",1)
point="  else raise_application_error(-20886,'LOAD_FLOOR_CONFIRMED_TOP_TYPE_REQUIRED');end if;"
insert="""  elsif node_value.get_string('kind')='STOCK'then
   select PALLET_TYPE_ID,TYPE_VERSION,LAST_OPERATION_ID into type_no,type_version,reference_value
    from RRL_PALLET_FLOOR_TYPE where UID_PALLET=root_id;
   RRL_STOCK_PLAN_HELPER.row_key(p_rows,'RRL_PALLET_FLOOR_TYPE',root_id);
   origin_value:='ROOT_STOCK_TYPE';
"""
assert point in s;s=s.replace(point,insert+point,1)
point="  result.put('root',root_id);"
s=s.replace(point,"  if type_version is not null then result.put('type_version',type_version);end if;\n"+point,1)
point="  else node_value.put('kind','CONTAINER');end if;"
assert point in s;s=s.replace(point,"  elsif frozen.get_string('type_origin')='ROOT_STOCK_TYPE'then node_value.put('kind','STOCK');\n"+point,1)
f[root+"005_loading_floor.sql"]=s
f[root+"007_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1201-stock-floor-type' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit full STOCK-pallet tare type through zero-quantity single Root command/version/scans and existing journal/outbox',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_schema.sql\n@@002_read.sql\n@@003_command.sql\n@@004_root.sql\n@@005_loading_floor.sql\n@@006_guard.sql\n@@007_ledger.sql\nalter package RRL_STOCK_HU_LOAD_CORE compile body;\n/\nalter package RRL_STOCK_TRIP_DEPART_CMD compile body;\n/\nalter package RRL_TRANSPORT_PLAN_RULES compile body;\n/\n"
f[root+"rollback.sql"]="begin\n raise_application_error(-20863,'Forward-only: retain declared pallet types, Root history/outbox and protected floor proofs; do not remove registration/guard after use');\nend;\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_PALLET_FLOOR_READ','RRL_STOCK_PALLET_TYPE_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_LOAD_FLOOR','RRL_PALLET_FLOOR_GUARD');\n"
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8");s=s.replace('self.command_type in {"INTERWARE_RECOVERY_CANCEL"','self.command_type in {"PALLET_FLOOR_TYPE_CONFIRM","INTERWARE_RECOVERY_CANCEL"',1);f[str(p)]=s
p=Path("wiki/database/nicora_ni022_stock_floor_type_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1202: private Root command and public scoped READ package prepared; one metadata table+existing Root journal, TYPEversion+scanCell/uid+explicit type/evidence, zero lines/units and unchanged stock/reserve, normal shared CFG/ROW20 fences. Root scope before cache, and current snapshot checked before write. StockPALLET schema untouched. LOAD type proof reads same metadata under same row lock. Native migration/application next; API/UI next.\n"
p=Path("wiki/index.md");f[str(p)]="- [Prepared1202: целая STOCK-паллета](database/nicora_ni022_stock_floor_type_20261014.md): zero-quantity Root type command/one metadata table/version/scan/same journal+outbox; no second stockwriter.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1202: prepared explicit fullSTOCKpallet normative type through existing Root; capture1201, metadata+privateguard/READscope/zeroeffect/historyoutbox/version/scans. Shared ROW20/CFG4, no RRL_PALLETS rowshape changes. Apply/API/UI next.\n"
print(json.dumps(f))
