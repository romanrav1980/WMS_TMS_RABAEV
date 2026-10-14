create or replace package RRL_STORE_MARK_CORE authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_READ,package RRL_STOCK_STORE_RECEIPT_CMD)as
 function source_proof(p_domain json_object_t)return json_object_t;
 function preview(p_domain json_object_t)return clob;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t);
 procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t);
 procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2);
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t);
end;
/

create or replace package body RRL_STORE_MARK_CORE as
 function source_proof(p_domain json_object_t)return json_object_t is
  tree json_object_t:=p_domain.get_object('snapshot');node json_object_t;proof json_object_t;profiles clob;n number;bad number;
  article varchar2(160);wire clob;
 begin
  if tree.get_array('nodes').get_size!=1 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;
  node:=treat(tree.get_array('nodes').get(0)as json_object_t);article:=node.get_string('article');
  wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_domain.get_string('load_operation_id'),node.get_string('uid'),tree.to_clob);proof:=json_object_t.parse(wire);
  select count(*),sum(case when SCAN_MODE='UNIT'then 0 else 1 end),
   json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into n,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article;
  if n<1 or n>50 or bad!=0 or proof.get_number('physical_unit_count')<1 then raise_application_error(-20886,'STORE_MARK_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  if n*proof.get_number('physical_unit_count')>20000 then raise_application_error(-20881,'STORE_MARK_SCAN_BOUND');end if;
  proof.put('profiles',json_array_t.parse(profiles));proof.put('supported',true);proof.put('expected_scan_count',n*proof.get_number('physical_unit_count'));return proof;
 end;
 function preview(p_domain json_object_t)return clob is p json_object_t;
 begin p:=source_proof(p_domain);return p.to_clob;
 exception when others then
  if sqlcode between -20999 and -20800 then p:=json_object_t();p.put('supported',false);p.put('reason',substr(sqlerrm,1,250));return p.to_clob;else raise;end if;
 end;
 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t)is
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
 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t)is node json_object_t;
 begin
  node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);
  RRL_STOCK_PLAN_HELPER.stock_closure(p_policies,p_resources,node.get_string('uid'),node.get_string('article'),p_domain.get_object('snapshot').get_string('cell'),null);
 end;
end;
/
