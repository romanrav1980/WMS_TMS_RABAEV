create or replace package RRL_STORE_AGG_SCAN authid definer accessible by(package RRL_STORE_MARK_CORE) as
 procedure normalize(p_proof clob,p_metadata clob,p_scans out clob);
end;
/
create or replace package body RRL_STORE_AGG_SCAN as
 procedure normalize(p_proof clob,p_metadata clob,p_scans out clob)is
  proof json_object_t:=json_object_t.parse(p_proof);m json_object_t:=json_object_t.parse(p_metadata);
  scans json_array_t:=json_array_t();aggregates json_array_t:=json_array_t();result json_array_t:=json_array_t();
  entry json_object_t;input json_object_t;entries json_array_t;expanded json_array_t;value json_object_t;
  wire clob;direct_wire clob;units_wire clob;expanded_wire clob;disposition varchar2(20);bad number;
 begin
  if m.has('unit_scans')then scans:=m.get_array('unit_scans');end if;
  if m.has('aggregation_scans')then aggregates:=m.get_array('aggregation_scans');end if;
  if scans is null or aggregates is null or scans.get_size>20000 or aggregates.get_size>1000 then raise_application_error(-20881,'STORE_AGG_SCAN_BOUND');end if;
  direct_wire:=scans.to_clob;units_wire:=proof.get_array('units').to_clob;
  -- Check the mode on the exact physical key, so equal profile names across SKUs do not prohibit UNIT evidence.
  select count(*)into bad from json_table(direct_wire,'$[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash'))scan_value
   join RRL_WMS_RECEIPT_CODE code on code.SYSTEM_CODE=scan_value.S and code.CODE_HASH=scan_value.H
   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=code.UID_PALLET and u.UNIT_ID=code.UNIT_ID
   join json_table(units_wire,'$[*]'columns(K varchar2(64)path '$.key',nested path '$.profiles[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',M varchar2(40)path '$.scan_mode')))expected
    on expected.K=u.PHYSICAL_UNIT_KEY and expected.S=scan_value.S and expected.P=scan_value.P where expected.M in('BOX','PALLET');
  if bad!=0 then raise_application_error(-20887,'STORE_AGGREGATION_ONLY_NO_UNIT_FALLBACK');end if;
  for i in 0..scans.get_size-1 loop result.append(scans.get(i));end loop;
  for i in 0..aggregates.get_size-1 loop
   entry:=treat(aggregates.get(i)as json_object_t).clone();disposition:=entry.get_string('disposition');
   if disposition is null or disposition not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20871,'STORE_AGG_DISPOSITION_REQUIRED');end if;
   entry.remove('disposition');input:=json_object_t();entries:=json_array_t();entries.append(entry);input.put('aggregation_scans',entries);wire:=input.to_clob;
   RRL_IW_AGG_SCAN.expand(wire,expanded_wire);expanded:=json_array_t.parse(expanded_wire);
   for j in 0..expanded.get_size-1 loop value:=treat(expanded.get(j)as json_object_t);value.put('disposition',disposition);result.append(value);end loop;
   if result.get_size>20000 then raise_application_error(-20881,'STORE_AGG_EXPANDED_BOUND');end if;
  end loop;
  p_scans:=result.to_clob;
 end;
end;
/
