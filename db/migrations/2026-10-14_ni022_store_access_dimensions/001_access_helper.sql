-- MIGRATION_ID: 2026-10-14-ni022-store-access-dimensions
create or replace package RRL_STORE_ACCESS_RULES as
 procedure check_sts(p_vehicle number,p_sts clob,p_complete number,p_result out clob);
 procedure assert_members(p_vehicle number,p_members clob);
end;
/
create or replace package body RRL_STORE_ACCESS_RULES as
 procedure check_addresses(p_vehicle number,p_addresses clob,p_complete number,p_result out clob)is
  profile json_object_t;physical json_object_t;outer_height number;outer_length number;
  result json_object_t:=json_object_t();rules json_array_t:=json_array_t();rule_value json_object_t;
  missing json_array_t:=json_array_t();profile_read boolean:=false;ready boolean:=false;n number:=0;
 begin
  if p_complete is null or p_complete not in(0,1)then raise_application_error(-20886,'STORE_ACCESS_COMPLETENESS_REQUIRED');end if;
  for r in(select cfg.STORE_ADDR,cfg.PROFILE_VERSION,cfg.MAX_VEHICLE_OUTER_HEIGHT_MM height_limit,
    cfg.MAX_VEHICLE_OUTER_LENGTH_MM length_limit,case when a.ADDR is null then 1 else nvl(a.DELETED3,0)end deleted
    from json_table(p_addresses,'$[*]'columns(address varchar2(255)path '$'))inputs
    join RRL_STORE_PROFILE cfg on cfg.STORE_ADDR=inputs.address
    left join RRL_ADDR a on a.ADDR=cfg.STORE_ADDR
    where cfg.MAX_VEHICLE_OUTER_HEIGHT_MM is not null or cfg.MAX_VEHICLE_OUTER_LENGTH_MM is not null
    order by cfg.STORE_ADDR fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'STORE_ACCESS_ADDRESS_BOUND_200');end if;
   if r.deleted!=0 then raise_application_error(-20886,'STORE_ACCESS_ADDRESS_INACTIVE');end if;
   if not profile_read then
    profile:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle));profile_read:=true;
    ready:=nvl(profile.get_string('state'),'~')='READY';
    if ready then physical:=profile.get_object('profile');outer_height:=physical.get_number('outer_height_mm');outer_length:=physical.get_number('outer_length_mm');end if;
   end if;
   rule_value:=json_object_t();rule_value.put('address',r.STORE_ADDR);rule_value.put('profile_version',r.PROFILE_VERSION);
   rule_value.put('max_vehicle_outer_height_mm',r.height_limit);rule_value.put('max_vehicle_outer_length_mm',r.length_limit);rules.append(rule_value);
   if not ready or(r.height_limit is not null and outer_height is null)or(r.length_limit is not null and outer_length is null)then
    if p_complete=1 then raise_application_error(-20886,'STORE_ACCESS_CURRENT_OUTER_DIMENSIONS_REQUIRED: '||substr(r.STORE_ADDR,1,255));end if;
    missing.append(r.STORE_ADDR);
   end if;
   if ready then
    if r.height_limit is not null and outer_height>r.height_limit then raise_application_error(-20886,'STORE_ACCESS_OUTER_HEIGHT_EXCEEDED: '||substr(r.STORE_ADDR,1,255));end if;
    if r.length_limit is not null and outer_length>r.length_limit then raise_application_error(-20886,'STORE_ACCESS_OUTER_LENGTH_EXCEEDED: '||substr(r.STORE_ADDR,1,255));end if;
   end if;
  end loop;
  result.put('vehicle_id',p_vehicle);result.put('rules',rules);result.put('missing_dimension_addresses',missing);
  result.put('requires_outer_dimensions',n>0);result.put('complete',missing.get_size=0);
  if profile_read then result.put('fleet_profile_version',profile.get_number('version'));result.put('fleet_profile_state',profile.get_string('state'));result.put('fleet_base_hash',profile.get_string('base_hash'));end if;
  result.put('outer_height_mm',outer_height);result.put('outer_length_mm',outer_length);p_result:=result.to_clob;
 end;
 procedure check_sts(p_vehicle number,p_sts clob,p_complete number,p_result out clob)is
  inputs json_array_t:=json_array_t.parse(p_sts);addresses json_array_t:=json_array_t();element_value json_element_t;
 begin
  if inputs.get_size>200 then raise_application_error(-20886,'STORE_ACCESS_ST_BOUND_200');end if;
  if inputs.get_size=0 then check_addresses(p_vehicle,addresses.to_clob,p_complete,p_result);return;end if;
  for i in 0..inputs.get_size-1 loop
   element_value:=inputs.get(i);
   if not element_value.is_string then raise_application_error(-20886,'STORE_ACCESS_ST_NUMBER_REQUIRED');end if;
   if inputs.get_string(i)is null or length(inputs.get_string(i))>100 then raise_application_error(-20886,'STORE_ACCESS_ST_NUMBER_REQUIRED');end if;
  end loop;
  for r in(select /*+ leading(inputs) use_nl(p) index(p) */ distinct p.ADDR from json_table(p_sts,'$[*]'columns(st_number varchar2(100)path '$'))inputs
    join RRL_SBORKA_PALLETS p on p.ST_NUMBER=inputs.st_number where p.ADDR is not null
    order by p.ADDR fetch first 201 rows only)loop
   if addresses.get_size>=200 then raise_application_error(-20886,'STORE_ACCESS_ADDRESS_BOUND_200');end if;addresses.append(r.ADDR);
  end loop;
  check_addresses(p_vehicle,addresses.to_clob,p_complete,p_result);
 end;
 procedure assert_members(p_vehicle number,p_members clob)is
  inputs json_array_t:=json_array_t.parse(p_members);addresses json_array_t:=json_array_t();element_value json_element_t;member_id number;result clob;n number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  if inputs.get_size<1 or inputs.get_size>200 then raise_application_error(-20886,'STORE_ACCESS_MEMBER_BOUND_200');end if;
  for i in 0..inputs.get_size-1 loop
   element_value:=inputs.get(i);if not element_value.is_number then raise_application_error(-20886,'STORE_ACCESS_MEMBER_ID_REQUIRED');end if;
   member_id:=inputs.get_number(i);if member_id is null or member_id<1 or member_id!=trunc(member_id)then raise_application_error(-20886,'STORE_ACCESS_MEMBER_ID_REQUIRED');end if;
  end loop;
  select /*+ leading(inputs) use_nl(p) index(p) */ count(*)into n from json_table(p_members,'$[*]'columns(id number path '$'))inputs
   left join RRL_SBORKA_PALLETS p on p.ID=inputs.id where p.ID is null;
  if n>0 then raise_application_error(-20886,'STORE_ACCESS_CURRENT_MEMBER_REQUIRED');end if;
  for r in(select distinct p.ADDR from json_table(p_members,'$[*]'columns(id number path '$'))inputs
    join RRL_SBORKA_PALLETS p on p.ID=inputs.id where p.ADDR is not null order by p.ADDR)loop addresses.append(r.ADDR);end loop;
  check_addresses(p_vehicle,addresses.to_clob,1,result);
 end;
end;
/
