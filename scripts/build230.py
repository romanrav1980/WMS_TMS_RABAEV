from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni053_marked_disposition");out={}
out[str(f/"001_schema.sql")]="""create table RRL_STORE_RECEIPT_UNIT(
 OPERATION_ID varchar2(100)not null,
 LOAD_OPERATION_ID varchar2(100)not null,
 PHYSICAL_UNIT_KEY varchar2(64)not null,
 UNIT_DISPOSITION varchar2(20)not null,
 BASE_QTY number(27,9)not null,
 BASE_UOM varchar2(20)not null,
 SOURCE_UNIT_VERSION number not null,
 RECORDED_BY nvarchar2(50)not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_STORE_RUNIT_PK primary key(OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_SOURCE_UK unique(LOAD_OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_FACT_FK foreign key(OPERATION_ID)references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 constraint RRL_STORE_RUNIT_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_STORE_RUNIT_UNIT_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_STATE_CK check(UNIT_DISPOSITION in('ACCEPTED','MISSING','REFUSED','DAMAGED')),
 constraint RRL_STORE_RUNIT_QTY_CK check(BASE_QTY>0 and SOURCE_UNIT_VERSION>=0)
);
"""
s=(f/"000_before_rrl_store_mark_core.sql").read_text(encoding="utf-8")
s=s.replace(" procedure declare_rows("," procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t);\n procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2);\n procedure declare_rows(",1)
start=s.index(" procedure verify_scans(",s.index("create or replace package body"))
end=s.index(" procedure declare_rows(",start)
s=s[:start]+""" procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t)is
 begin p_proof:=source_proof(p_domain);end;
 function tuple_key(p_unit varchar2,p_system varchar2,p_profile varchar2)return varchar2 is
 begin return rawtohex(RRL_STOCK_LOCK_API.resource_key('STOREMARK',p_unit,rawtohex(RRL_STOCK_LOCK_API.resource_key('PROFILE',p_system,p_profile))));end;
 procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t)is
  units json_array_t:=p_proof.get_array('units');profiles json_array_t:=p_proof.get_array('profiles');scans json_array_t:=json_array_t();
  unit_value json_object_t;profile_value json_object_t;scan_value json_object_t;line_value json_object_t;result_value json_object_t;
  type marks_map is table of number index by varchar2(4000);expected marks_map;resolved marks_map;coverage marks_map;
  type state_map is table of varchar2(20)index by varchar2(64);states state_map;
  k varchar2(4000);unit_key varchar2(64);disposition varchar2(20);wire clob;resolved_count number:=0;
  accepted number:=0;missing number:=0;refused number:=0;damaged number:=0;qty number;profile_count number:=profiles.get_size;
  function nonnegative(p_text varchar2)return number is
  begin if regexp_like(p_text,'^0{1,18}([.]0{1,9})?$')then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end;
 begin
  if p_metadata.has('unit_scans')then scans:=p_metadata.get_array('unit_scans');end if;
  if scans.get_size>20000 or p_lines.get_size!=1 then raise_application_error(-20881,'STORE_MARK_DISPOSITION_BOUND');end if;
  for i in 0..units.get_size-1 loop
   unit_value:=treat(units.get(i)as json_object_t);unit_key:=unit_value.get_string('key');coverage(unit_key):=0;states(unit_key):='MISSING';
   for j in 0..profiles.get_size-1 loop
    profile_value:=treat(profiles.get(j)as json_object_t);expected(tuple_key(unit_key,profile_value.get_string('system_code'),profile_value.get_string('profile_code'))):=0;
   end loop;
  end loop;
  for i in 0..scans.get_size-1 loop
   scan_value:=treat(scans.get(i)as json_object_t);
   if scan_value.get_string('system_code')is null or scan_value.get_string('profile_code')is null or not regexp_like(scan_value.get_string('code_hash'),'^[a-f0-9]{64}$')then raise_application_error(-20871,'STORE_MARK_SCAN_INVALID');end if;
   disposition:=nvl(scan_value.get_string('disposition'),'ACCEPTED');
   if disposition not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20871,'STORE_MARK_PHYSICAL_SCAN_DISPOSITION_REQUIRED');end if;
  end loop;
  wire:=scans.to_clob;
  for z in(select j.I,j.S,j.P,nvl(j.D,'ACCEPTED')D,u.PHYSICAL_UNIT_KEY from
   json_table(wire,'$[*]'columns(I for ordinality,S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash',D varchar2(20)path '$.disposition'))j
   join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.S and c.CODE_HASH=j.H
   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
   where u.STOCK_STATUS='ISSUED'and exists(select 1 from json_table(c.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile'))pr where pr.P=j.P))loop
   k:=tuple_key(z.PHYSICAL_UNIT_KEY,z.S,z.P);
   if not expected.exists(k)then raise_application_error(-20886,'STORE_MARK_FOREIGN_UNIT_OR_PROFILE');end if;
   if resolved.exists(to_char(z.I))or expected(k)=1 then raise_application_error(-20871,'STORE_MARK_DUPLICATE_SCAN');end if;
   if coverage(z.PHYSICAL_UNIT_KEY)>0 and states(z.PHYSICAL_UNIT_KEY)!=z.D then raise_application_error(-20886,'STORE_MARK_ONE_UNIT_DISPOSITION_REQUIRED');end if;
   resolved(to_char(z.I)):=1;expected(k):=1;coverage(z.PHYSICAL_UNIT_KEY):=coverage(z.PHYSICAL_UNIT_KEY)+1;states(z.PHYSICAL_UNIT_KEY):=z.D;resolved_count:=resolved_count+1;
  end loop;
  if resolved_count!=scans.get_size then raise_application_error(-20886,'STORE_MARK_FOREIGN_CODE');end if;
  p_units:=json_array_t();
  for i in 0..units.get_size-1 loop
   unit_value:=treat(units.get(i)as json_object_t);unit_key:=unit_value.get_string('key');disposition:=states(unit_key);qty:=RRL_STOCK_MATH.quantity(unit_value.get_string('quantity'));
   if coverage(unit_key)>0 and coverage(unit_key)!=profile_count then raise_application_error(-20886,'STORE_MARK_ALL_UNIT_PROFILES_REQUIRED');end if;
   if disposition='ACCEPTED'then accepted:=accepted+qty;elsif disposition='MISSING'then missing:=missing+qty;elsif disposition='REFUSED'then refused:=refused+qty;else damaged:=damaged+qty;end if;
   result_value:=unit_value.clone();result_value.put('disposition',disposition);p_units.append(result_value);
  end loop;
  line_value:=treat(p_lines.get(0)as json_object_t);
  if nonnegative(line_value.get_string('accepted'))!=accepted or nonnegative(line_value.get_string('missing'))!=missing or nonnegative(line_value.get_string('refused'))!=refused or nonnegative(line_value.get_string('damaged'))!=damaged or nonnegative(line_value.get_string('extra'))!=0 then raise_application_error(-20886,'STORE_MARK_EXACT_UNIT_DISPOSITION_QUANTITY_REQUIRED');end if;
 end;
 procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2)is
  x json_object_t;key_value varchar2(64);state_value varchar2(20);qty number;uom varchar2(20);version_value number;
 begin
  for i in 0..p_units.get_size-1 loop
   x:=treat(p_units.get(i)as json_object_t);key_value:=x.get_string('key');state_value:=x.get_string('disposition');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom:=x.get_string('base_uom');version_value:=x.get_number('version');
   insert into RRL_STORE_RECEIPT_UNIT(OPERATION_ID,LOAD_OPERATION_ID,PHYSICAL_UNIT_KEY,UNIT_DISPOSITION,BASE_QTY,BASE_UOM,SOURCE_UNIT_VERSION,RECORDED_BY)
    values(p_operation,p_load,key_value,state_value,qty,uom,version_value,p_actor);
  end loop;
 end;
"""+s[end:]
out[str(f/"002_mark_core.sql")]=s
s=(f/"000_before_rrl_stock_store_receipt_cmd.sql").read_text(encoding="utf-8")
s=s.replace("weight_issue boolean;","weight_issue boolean;unit_dispositions json_array_t;unit_value json_object_t;",1)
s=s.replace("  if v.has('marked_unit_proof')and has_issue then raise_application_error(-20886,'STORE_MARKED_DISPOSITION_UNIT_ASSIGNMENT_REQUIRED');end if;","""  if v.has('marked_unit_proof')then
   RRL_STORE_MARK_CORE.resolve_disposition(v.get_object('marked_unit_proof'),m,disposition,unit_dispositions);v.put('marked_unit_dispositions',unit_dispositions);
   for i in 0..unit_dispositions.get_size-1 loop unit_value:=treat(unit_dispositions.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_UNIT',p_operation||':'||unit_value.get_string('key'));end loop;
  end if;""",1)
s=s.replace("weight_issue boolean;","weight_issue boolean;fresh_units json_array_t;",1 if False else 0) if False else s
# Second procedure's declarations, independent from compile declarations.
s=s.replace("fresh_weight json_object_t;weight_issue boolean;","fresh_weight json_object_t;weight_issue boolean;fresh_units json_array_t;")
s=s.replace("  if v.has('marked_unit_proof')and has_issue then raise_application_error(-20886,'STORE_MARKED_DISPOSITION_UNIT_ASSIGNMENT_REQUIRED');end if;","""  if v.has('marked_unit_proof')then
   RRL_STORE_MARK_CORE.resolve_disposition(now_v.get_object('marked_unit_proof'),m,fresh_disposition,fresh_units);
   if dbms_lob.compare(fresh_units.to_clob,v.get_array('marked_unit_dispositions').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: store unit disposition');end if;
  end if;""",1)
s=s.replace("  RRL_STOCK_STORE_DISPOSITION.persist(op,v,p_actor,lines);","  RRL_STOCK_STORE_DISPOSITION.persist(op,v,p_actor,lines);\n  if v.has('marked_unit_dispositions')then RRL_STORE_MARK_CORE.persist(op,load_op,v.get_array('marked_unit_dispositions'),p_actor);j.put('unit_dispositions',v.get_array('marked_unit_dispositions'));end if;")
out[str(f/"003_receipt.sql")]=s
out[str(f/"004_guard.sql")]="""create or replace trigger RRL_STORE_RECEIPT_UNIT_GUARD before insert or update or delete on RRL_STORE_RECEIPT_UNIT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_APPEND_ONLY');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or:new.RECORDED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RECEIPT_UNIT',op||':'||:new.PHYSICAL_UNIT_KEY));
 select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain.marked_unit_dispositions[*]'columns(K varchar2(64)path '$.key',D varchar2(20)path '$.disposition',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))u
  on u.K=:new.PHYSICAL_UNIT_KEY and u.D=:new.UNIT_DISPOSITION and RRL_STOCK_MATH.quantity(u.Q)=:new.BASE_QTY and u.B=:new.BASE_UOM and u.V=:new.SOURCE_UNIT_VERSION
  where o.OPERATION_ID=op and o.COMMAND_TYPE='STORE_RECEIPT'and o.STATE='IN_FLIGHT'and json_value(o.RESOLVED_PLAN_JSON,'$.domain.load_operation_id')=:new.LOAD_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'STORE_UNIT_DISPOSITION_FROZEN_PLAN_REQUIRED');end if;
end;
/
"""
s=(f/"000_before_rrl_stock_store_receipt_read.sql").read_text(encoding="utf-8")
s=s.replace("j.put('marked_unit_control',json_object_t.parse(RRL_STORE_MARK_CORE.preview(j)));","j.put('marked_unit_control',json_object_t.parse(RRL_STORE_MARK_CORE.preview(j)));j.put('marked_partial_control',true);")
out[str(f/"005_reader.sql")]=s
out[str(f/"006_recompile.sql")]="alter package RRL_STOCK_STORE_RECEIPT_READ compile body;\nalter package RRL_STOCK_STORE_RECEIPT_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_STORE_RECEIPT_UNIT;if n>0 then raise_application_error(-20863,'MARKED_UNIT_DISPOSITION_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_store_mark_core.sql\n@@000_before_rrl_stock_store_receipt_cmd.sql\n@@000_before_rrl_stock_store_receipt_read.sql\n@@006_recompile.sql\ndrop trigger RRL_STORE_RECEIPT_UNIT_GUARD;\ndrop table RRL_STORE_RECEIPT_UNIT;\n"
out["wiki/database/nicora_ni053_marked_disposition_design_20261011.md"]="# NI05.3: физическая единица в расхождении получателя\n230 adds immutable per-unit receipt disposition ACCEPTED/MISSING/REFUSED/DAMAGED tied original issued unit key/version/qty/UOM/load. Codes scanned in each mandatory profile must agree on one disposition per unit; absent whole units are MISSING, incomplete per-profile unit rejected. Sum exact physical base quantities must equal original legacy disposition line; extra units cannot be silently created. Existing receipt/discrepancy/obligations/outbox remain atomic with new facts/no warehouse P/H changes/no new unit birth or GovACK. Fresh source checkpoint/paired empty-table rollback; forward repair after facts.\n"
print(json.dumps(out,ensure_ascii=True))
