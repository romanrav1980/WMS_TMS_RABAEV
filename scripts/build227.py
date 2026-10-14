raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_placement");out={}
s=(f/"000_before_rrl_stock_interware_put.sql").read_text(encoding="utf-8")
s=s.replace(" procedure compile_command("," procedure assert_scope(p_receipt varchar2,p_actor varchar2);\n procedure compile_command(",1)
s=s.replace("package body RRL_STOCK_INTERWARE_PUT as","""package body RRL_STOCK_INTERWARE_PUT as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;
 end;""")
s=s.replace("v_gross number;n number;","v_gross number;n number;unit_wire clob;unit_snapshot clob;unit_count number;unit_total number;unit_distinct number;")
s=s.replace("if n!=0 then raise_application_error(-20886,'INTERWARE_MARKED_PLACEMENT_FLOW_REQUIRED');end if;","""select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=receipt.ROOT_UID;
 if n>0 or unit_count>0 then
  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;
  select count(*),sum(u.BASE_QTY),count(distinct u.PHYSICAL_UNIT_KEY),
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)returning clob)
   into n,unit_total,unit_distinct,unit_snapshot
   from RRL_WMS_RECEIPT_UNIT u join json_table(unit_wire,'$.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=receipt.ROOT_UID and u.CURRENT_CELL=receipt.RECEIVE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM;
  if unit_count<1 or unit_count>10000 or n!=unit_count or unit_distinct!=unit_count or unit_total!=receipt.BASE_QTY or json_object_t.parse(unit_wire).get_number('physical_unit_count')!=unit_count then raise_application_error(-20884,'INTERWARE_ORIGINAL_AVAILABLE_UNITS_REQUIRED');end if;
 end if;""")
# Stable sort is part of snapshot contract.
s=s.replace("'version'value u.UNIT_VERSION)returning clob)","'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)")
s=s.replace("p_domain:=json_object_t();","p_domain:=json_object_t();if unit_snapshot is not null then p_domain.put('physical_units',json_array_t.parse(unit_snapshot));end if;",1)
out[str(f/"001_placement.sql")]=s
root=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
needle="  if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE')then"
root=root.replace(needle,"  if g_kind='INTERWARE_PUTAWAY_PLAN'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_PUT.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor);end;end if;\n"+needle)
out[str(f/"002_root.sql")]=root
out[str(f/"003_recompile.sql")]="alter package RRL_STOCK_TASK_PLAN compile body;\nalter package RRL_STOCK_TASK_CORE compile body;\nalter package RRL_STOCK_TASK_DOMAIN compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_INTERWARE_PLACEMENT p join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNIT_MANIFEST m on m.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID;if n>0 then raise_application_error(-20863,'MARKED_PLACEMENT_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_stock_interware_put.sql\n@@000_before_rrl_stock_posting_api.sql\n@@003_recompile.sql\n"
out["wiki/database/retailcase_ni061_marked_placement_design_20261011.md"]="# NI06.1: размещение исходного маркированного состава\n227 removes only old explicit marking refusal in original INTERWARE task owner. Exact frozen225 keys/quantity/UOM plus current whole AVAILABLE/no-HARD/sourcecell/versioned unit snapshot; existing original task/stock version/docks/capacity conserved. Existing transfer owner already moves units atomically with P/H, no duplicate mover. Current target scope before replay. Fresh affected-owner checkpoints, forward repair after marked placement.\n"
print(json.dumps(out,ensure_ascii=True))
