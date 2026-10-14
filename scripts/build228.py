raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_onward");out={}
s=(f/"000_before_rrl_stock_interware_next.sql").read_text(encoding="utf-8")
s=s.replace("v_policy number;n number;","v_policy number;n number;unit_count number;unit_total number;unit_distinct number;unit_wire clob;unit_snapshot clob;")
s=s.replace("if n!=0 then raise_application_error(-20886,'INTERWARE_ONWARD_MARKED_FLOW_REQUIRED');end if;","""select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=receipt.ROOT_UID;
 if n>0 or unit_count>0 then
  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;
  select count(*),sum(u.BASE_QTY),count(distinct u.PHYSICAL_UNIT_KEY),
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,unit_total,unit_distinct,unit_snapshot
   from RRL_WMS_RECEIPT_UNIT u join json_table(unit_wire,'$.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=receipt.ROOT_UID and u.CURRENT_CELL=bind.SOURCE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM;
  if unit_count<1 or unit_count>10000 or n!=unit_count or unit_distinct!=unit_count or unit_total!=receipt.BASE_QTY or json_object_t.parse(unit_wire).get_number('physical_unit_count')!=unit_count then raise_application_error(-20884,'INTERWARE_ONWARD_ORIGINAL_UNITS_REQUIRED');end if;
  j.put('physical_units',json_array_t.parse(unit_snapshot));
 end if;""")
out[str(f/"001_onward.sql")]=s
custody=(f/"000_before_rrl_stock_interware_custody.sql").read_text(encoding="utf-8").replace(" procedure compile_command("," procedure assert_scope(p_receipt varchar2,p_actor varchar2);\n procedure compile_command(",1)
custody=custody.replace("package body RRL_STOCK_INTERWARE_CUSTODY as","""package body RRL_STOCK_INTERWARE_CUSTODY as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_CUSTODY_ACTOR_REQUIRED');end if;
 end;""")
out[str(f/"002_custody.sql")]=custody
root=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
needle="  if g_kind='INTERWARE_PUTAWAY_PLAN'then"
root=root.replace(needle,"  if g_kind='INTERWARE_CUSTODY_RELEASE'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_CUSTODY.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor);end;end if;\n"+needle)
root=root.replace("   elsif g_kind='RESERVATION_ALLOCATE_POOL'", "   elsif g_kind='STORE_RETURN_DISPOSE' then RRL_STOCK_RETURN_DISPOSE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='RESERVATION_ALLOCATE_POOL'",1)
root=root.replace("  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command","  elsif g_kind='STORE_RETURN_DISPOSE' then RRL_STOCK_RETURN_DISPOSE.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command",1)
out[str(f/"003_root.sql")]=root
out[str(f/"004_recompile.sql")]="alter package RRL_STOCK_SHIPPING_CORE compile body;\nalter package RRL_STOCK_SINGLE_LOAD_CMD compile body;\nalter package RRL_STOCK_LOADING_READ compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_INTERWARE_ONWARD_DISPATCH d join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNIT_MANIFEST m on m.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID;if n>0 then raise_application_error(-20863,'MARKED_ONWARD_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_stock_interware_next.sql\n@@000_before_rrl_stock_interware_custody.sql\n@@000_before_rrl_stock_posting_api.sql\n@@004_recompile.sql\n"
out["wiki/database/nicora_ni061_marked_onward_design_20261011.md"]="# NI06.1: исходные маркированные единицы во втором плече\n228 keeps original onward ST constructor/assignment/ShippingCore/QC/SINGLE loader. Exact225 immutable unit set/current AVAILABLE/no HARD/whole quantity/sourcecell/versioned snapshot replaces marked source refusal. Existing stock_closure declares UNIT locks, existing native effect issues same units. Custody current actor before replay, old first departure/fulfillment retained/no second fulfillment. Restores missing existing STORE_RETURN_DISPOSE handler (manifest-owner coverage found one missing). Fresh owner sources and rollback before application; forward repair after marked onward dispatch.\n"
print(json.dumps(out,ensure_ascii=True))
