raise SystemExit("Retired authoring generator: use final225 SQL/fresh checkpoints; never overwrite live source or proof schema")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_source");out={}
out["wiki/database/nicora_ni061_marked_source_design_20261011.md"]="""# NI06.1: точный маркированный состав исходного плеча
225 extends existing standalone STOCK/FULLPAL source plan. Source actually DEPARTED/existing original ST/one whole leaf, no current P/H/store receipt retained. Exact original native physical-before unit signature must match sorted current ISSUED/no-HARD units at archived source cell; quantity/UOM/root/physical count exact, max10000. Current SKU marking/profile/serialized applicability requires captured units. WMS physical units with multiple systems remain one quantity; immutable code identity retained. Existing plan stores original source composition, metadata-only/no stock birth. Current source warehouse/dispatcher checked before plan replay; separate receiving command still refuses marked until next225 receiving extension, no premature availability or legal ACK.
"""
out[str(f/"001_unit_source.sql")]="""create or replace package RRL_INTERWARE_UNIT_SOURCE authid definer as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob;
end;
/
create or replace package body RRL_INTERWARE_UNIT_SOURCE as
 procedure assert_scope(p_load varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_TT_HU_LOAD_FACT lf join RUSERS u on u.ID=p_actor
   where lf.LOAD_OPERATION_ID=p_load and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or u.WARE_ID=lf.WARE_ID);
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_SOURCE_DISPATCHER_REQUIRED');end if;
 end;
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob is
  tree json_object_t:=json_object_t.parse(p_snapshot);node json_object_t;plain json_array_t:=json_array_t();units json_array_t:=json_array_t();x json_object_t;j json_object_t:=json_object_t();finger json_object_t:=json_object_t();
  wire clob;expected varchar2(64);actual varchar2(64);cell_value varchar2(60);uom_value varchar2(20);qty number;total number:=0;n number:=0;required_count number;proof_count number;
 begin
  if tree.get_array('nodes').get_size!=1 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_PHYSICAL_ROOT_REQUIRED');end if;
  node:=treat(tree.get_array('nodes').get(0)as json_object_t);cell_value:=tree.get_string('cell');uom_value:=node.get_string('base_uom');qty:=RRL_STOCK_MATH.quantity(node.get_string('quantity'));
  if node.get_string('kind')!='STOCK'or node.get_string('uid')!=p_uid or cell_value is null or uom_value is null then raise_application_error(-20886,'INTERWARE_ORIGINAL_STOCK_SOURCE_REQUIRED');end if;
  select count(*)into required_count from RRL_PALLETS p where p.UID_PALLET=p_uid and(exists(select 1 from RRL_SKU_RECEIPT_PROFILE profile where profile.ARTICUL=p.ARTICUL)or exists(select 1 from RRL_SKU_RECEIPT_POLICY policy where policy.ARTICUL=p.ARTICUL and(policy.MARKING_REQUIRED=1 or policy.SERIALIZED_WEIGHT_BOXES=1))or exists(select 1 from RRL_FINISHED_GOODS_SKU fg where fg.ARTICUL=p.ARTICUL and fg.CRPT_REQUIRED=1));
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,CURRENT_CELL,UNIT_VERSION,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid order by PHYSICAL_UNIT_KEY fetch first 10001 rows only)loop
   n:=n+1;if n>10000 or u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY<=0 or u.BASE_UOM is null or u.BASE_UOM!=uom_value or u.CURRENT_CELL is null or u.CURRENT_CELL!=cell_value or u.STOCK_STATUS!='ISSUED'or u.HARD_RESERVATION_ID is not null or u.UNIT_VERSION is null then raise_application_error(-20884,'INTERWARE_ORIGINAL_ISSUED_UNIT_SET_REQUIRED');end if;
   x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);plain.append(x.clone());x.put('version',u.UNIT_VERSION);units.append(x);total:=total+u.BASE_QTY;
  end loop;
  if n!=nvl(tree.get_number('physical_unit_count'),0)or(n>0 and total!=qty)or(required_count>0 and n=0)then raise_application_error(-20884,'INTERWARE_EXACT_MARKED_SOURCE_QUANTITY_REQUIRED');end if;
  if n>0 then
   select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED';
   select count(*),max(S)into proof_count,expected from json_table(wire,'$.physical_before[*]'columns(U varchar2(150)path '$.uid',S varchar2(64)path '$.unit_signature'))where U=p_uid;
   if proof_count!=1 or expected is null then raise_application_error(-20884,'INTERWARE_ORIGINAL_UNIT_FINGERPRINT_REQUIRED');end if;
   finger.put('units',plain);actual:=rawtohex(sys.dbms_crypto.hash(finger.to_clob,sys.dbms_crypto.hash_sh256));
   if actual!=expected then raise_application_error(-20884,'INTERWARE_ORIGINAL_UNIT_FINGERPRINT_CONFLICT');end if;
   j.put('unit_signature',actual);
  end if;
  j.put('units',units);j.put('physical_unit_count',n);j.put('unit_capture_required',n>0);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('base_uom',uom_value);j.put('source_cell',cell_value);return j.to_clob;
 end;
end;
/
"""
s=(f/"000_before_rrl_interware_plan_guard.sql").read_text(encoding="utf-8")
s=s.replace("declare n number;","declare n number;unit_wire clob;",1)
start=s.index(" select count(*)into n from RRL_PALLETS p where p.UID_PALLET=:new.ROOT_UID and(")
end=s.index(" select count(*)into n from RRL_STORE_RECEIPT_FACT",start)
s=s[:start]+" unit_wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:new.SOURCE_LOAD_OPERATION_ID,:new.ROOT_UID,:new.SOURCE_COMPOSITION_JSON);\n"+s[end:];out[str(f/"002_plan_guard.sql")]=s
out[str(f/"apply.sql")]="@@001_unit_source.sql\n@@002_plan_guard.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_INTERWARE_PLAN where nvl(json_value(SOURCE_COMPOSITION_JSON,'$.physical_unit_count' returning number),0)>0;if n>0 then raise_application_error(-20863,'MARKED_INTERWARE_PLAN_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_interware_plan_guard.sql
drop package RRL_INTERWARE_UNIT_SOURCE;
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
anchor='                cur.execute("select PAYLOAD_HASH,RESULT_JSON';idx=s.index(anchor);s=s[:idx]+'                cur.callproc("RRL_INTERWARE_UNIT_SOURCE.assert_scope",[source_load,actor])\n'+s[idx:]
anchor='                cur.setinputsizes(result_body=';idx=s.index(anchor)
s=s[:idx]+'''                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:load_id,:root_id,:snapshot) from dual",
                            load_id=source_load,root_id=source[2],snapshot=source[3])
                unit_source=read_oracle_json(cur.fetchone()[0])
                if unit_source["physical_unit_count"]:
                    result.update(physical_unit_count=unit_source["physical_unit_count"],unit_capture_required=True,
                                  original_unit_signature=unit_source["unit_signature"],regulatory_ack_verified=False)
'''+s[idx:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
