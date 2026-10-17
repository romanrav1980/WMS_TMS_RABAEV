-- PREPARED ONLY. Caller MUST establish SET TRANSACTION READ ONLY first.
create or replace package body RRL_SHIPPING_GROSS_READ as
 function digest(p_value clob)return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(p_value,sys.dbms_crypto.hash_sh256));end;
 function ordered(p_left varchar2,p_right varchar2)return boolean is
  l raw(32767):=utl_i18n.string_to_raw(p_left,'AL32UTF8');r raw(32767):=utl_i18n.string_to_raw(p_right,'AL32UTF8');
  pos number;common_length number;
 begin
  pos:=utl_raw.compare(l,r);common_length:=least(nvl(utl_raw.length(l),0),nvl(utl_raw.length(r),0));
  if pos=0 or pos>common_length then return nvl(utl_raw.length(l),0)<nvl(utl_raw.length(r),0);end if;
  return to_number(rawtohex(utl_raw.substr(l,pos,1)),'XX')<to_number(rawtohex(utl_raw.substr(r,pos,1)),'XX');
 end;
 function canon(p_value json_element_t,p_depth number default 0)return json_element_t is
  o json_object_t;r json_object_t:=json_object_t();a json_array_t;b json_array_t:=json_array_t();keys json_key_list;swap varchar2(4000);
 begin
  if p_depth>32 then raise_application_error(-20881,'SHIPPING_GROSS_JSON_DEPTH_BOUND');end if;
  if p_value.is_object then
   o:=treat(p_value as json_object_t);keys:=o.get_keys;
   for i in 1..keys.count loop for j in i+1..keys.count loop
    if ordered(keys(j),keys(i))then swap:=keys(i);keys(i):=keys(j);keys(j):=swap;end if;
   end loop;end loop;
   for i in 1..keys.count loop r.put(keys(i),canon(o.get(keys(i)),p_depth+1));end loop;return r;
  elsif p_value.is_array then
   a:=treat(p_value as json_array_t);if a.get_size>10000 then raise_application_error(-20881,'SHIPPING_GROSS_ARRAY_BOUND');end if;
   if a.get_size>0 then for i in 0..a.get_size-1 loop b.append(canon(a.get(i),p_depth+1));end loop;end if;return b;
  end if;return p_value;
 end;
 function ordered_raw(l raw,r raw)return boolean is pos binary_integer;common_length binary_integer;
 begin
  pos:=utl_raw.compare(l,r);common_length:=least(nvl(utl_raw.length(l),0),nvl(utl_raw.length(r),0));
  if pos=0 or pos>common_length then return nvl(utl_raw.length(l),0)<nvl(utl_raw.length(r),0);end if;
  return to_number(rawtohex(utl_raw.substr(l,pos,1)),'XX')<to_number(rawtohex(utl_raw.substr(r,pos,1)),'XX');
 end;
 function sorted(a json_array_t,p_kind varchar2 default 'SMALL')return json_array_t is
  type value_list is table of json_element_t index by binary_integer;
  type raw_list is table of raw(32767)index by binary_integer;
  values_list value_list;scratch value_list;keys raw_list;key_scratch raw_list;
  n binary_integer:=a.get_size;width binary_integer:=1;lo binary_integer;mid binary_integer;hi binary_integer;
  left_no binary_integer;right_no binary_integer;chosen binary_integer;
  item json_element_t;obj json_object_t;r json_array_t:=json_array_t();key_text varchar2(32767);
  wire clob;work_chars number:=0;item_chars number;
 begin
  if n>1000 or p_kind not in('SMALL','NODES','SHIPMENTS')then raise_application_error(-20881,'SHIPPING_GROSS_SORT_BOUND');end if;
  if n>0 then
   -- Reject work before recursive canonicalization. CLOB lengths are characters.
   for i in 1..n loop
    wire:=a.get(i-1).to_clob;item_chars:=dbms_lob.getlength(wire);work_chars:=work_chars+item_chars;
    if item_chars>131072 or work_chars>2097152 then raise_application_error(-20881,'SHIPPING_GROSS_SORT_WORK_BOUND');end if;
    if p_kind='SMALL'and item_chars>8191 then raise_application_error(-20881,'SHIPPING_GROSS_SMALL_SORT_ITEM_BOUND');end if;
   end loop;
   for i in 1..n loop
    item:=canon(a.get(i-1));values_list(i):=item;
    if p_kind='NODES'then obj:=treat(item as json_object_t);key_text:=obj.get_string('uid');
    elsif p_kind='SHIPMENTS'then obj:=treat(item as json_object_t);key_text:=RRL_STOCK_PLAN_HELPER.decimal_text(obj.get_number('document_id'));
    else key_text:=item.to_string;end if;
    if key_text is null then raise_application_error(-20886,'SHIPPING_GROSS_SORT_ID_REQUIRED');end if;
    keys(i):=utl_i18n.string_to_raw(key_text,'AL32UTF8');
   end loop;
   while width<n loop
    lo:=1;
    while lo<=n loop
     mid:=least(lo+width-1,n);hi:=least(lo+2*width-1,n);left_no:=lo;right_no:=mid+1;
     for k in lo..hi loop
      if left_no<=mid and(right_no>hi or not ordered_raw(keys(right_no),keys(left_no)))then chosen:=left_no;left_no:=left_no+1;
      else chosen:=right_no;right_no:=right_no+1;end if;
      scratch(k):=values_list(chosen);key_scratch(k):=keys(chosen);
     end loop;
     lo:=hi+1;
    end loop;
    values_list:=scratch;keys:=key_scratch;scratch.delete;key_scratch.delete;width:=width*2;
   end loop;
   for i in 1..n loop
    if p_kind!='SMALL'and i>1 and utl_raw.length(keys(i))=utl_raw.length(keys(i-1))and utl_raw.compare(keys(i),keys(i-1))=0 then raise_application_error(-20886,'SHIPPING_GROSS_SORT_ID_DUPLICATE');end if;
    r.append(values_list(i));
   end loop;
  end if;return r;
 end;
 function project_node(o json_object_t)return json_object_t is r json_object_t:=json_object_t();names json_array_t:=json_array_t('["uid","kind","type","version","sscc","cell","case_task_id","article","quantity","hard_quantity","base_uom","stock_version","tare_weight_kg"]');key_value varchar2(100);
 begin
  for i in 0..names.get_size-1 loop key_value:=names.get_string(i);if o.has(key_value)then r.put(key_value,o.get(key_value));end if;end loop;return r;
 end;
 procedure freeze(p_source clob,p_actor nvarchar2,p_result out clob)is
  input_value json_object_t;snapshot_value json_object_t;root_value json_object_t;projection json_object_t:=json_object_t();result_value json_object_t:=json_object_t();
  node_values json_array_t;nodes json_array_t:=json_array_t();shipments json_array_t:=json_array_t();compiled json_object_t;entry json_object_t;request_value json_object_t:=json_object_t();source_value json_object_t:=json_object_t();metadata_value json_object_t:=json_object_t();
  p clob;r clob;d clob;wire clob;identifier_value varchar2(200);alias_value varchar2(32);ware_value number;n number;now_value timestamp with time zone:=systimestamp;keys json_key_list;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'SHIPPING_GROSS_OUTSIDE_STOCK_REQUIRED');end if;
  if p_actor is null or p_source is null or dbms_lob.getlength(p_source)>2000 then raise_application_error(-20881,'SHIPPING_GROSS_INPUT_BOUND');end if;
  input_value:=json_object_t.parse(p_source);keys:=input_value.get_keys;
  if keys.count!=3 then raise_application_error(-20886,'SHIPPING_GROSS_MASS_FREE_EXACT_INPUT');end if;
  for i in 1..keys.count loop if keys(i)not in('handling_unit_identifier','scan_container','expected_root_version')then raise_application_error(-20886,'SHIPPING_GROSS_MASS_FREE_EXACT_INPUT');end if;end loop;
  identifier_value:=input_value.get_string('handling_unit_identifier');
  if identifier_value is null or length(identifier_value)>200 or input_value.get_string('scan_container')is null
   or input_value.get_number('expected_root_version')is null or input_value.get_number('expected_root_version')<0
   or input_value.get_number('expected_root_version')!=trunc(input_value.get_number('expected_root_version'))then raise_application_error(-20886,'SHIPPING_GROSS_IDENTIFIERS_REQUIRED');end if;
  select count(*)into n from RRL_PALLETS where UID_PALLET=identifier_value or SSCC=identifier_value;
  if n!=1 then raise_application_error(-20886,'SHIPPING_GROSS_UNIQUE_IDENTIFIER_REQUIRED');end if;
  select UID_PALLET,SSCC into identifier_value,alias_value from RRL_PALLETS where UID_PALLET=identifier_value or SSCC=identifier_value;
  if input_value.get_string('scan_container')!=identifier_value and(alias_value is null or input_value.get_string('scan_container')!=alias_value)then raise_application_error(-20886,'SHIPPING_GROSS_PHYSICAL_SCAN_REQUIRED');end if;
  -- Resolve physical WARE before exposing closure; assert existing current owner policy, including WARE/GROUP.
  select c.WARE_ID into ware_value from RRL_PALLETS p join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL where p.UID_PALLET=identifier_value and p.HU_KIND='CONTAINER';
  if ware_value is null then raise_application_error(-20886,'SHIPPING_GROSS_PHYSICAL_WARE_REQUIRED');end if;
  if nvl(RRL_ACCESS_API.allowed(p_actor,'warehouse_task_view','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(ware_value),null),0)!=1 then
   raise_application_error(-20882,'SHIPPING_GROSS_VIEW_FORBIDDEN');
  end if;
  source_value.put('uid',identifier_value);metadata_value.put('expected_version',input_value.get_number('expected_root_version'));
  request_value.put('command_type','HU_SHIP');request_value.put('operation_id','SHIPPING.GROSS.READ');request_value.put('source',source_value);request_value.put('metadata',metadata_value);
  -- Existing compile is pure: policy/resource declaration only. Existing child QC remains required.
  RRL_STOCK_HU_SHIP_CMD.compile_command(request_value.to_clob,'SHIPPING.GROSS.READ',p,r,d);
  compiled:=json_object_t.parse(d);snapshot_value:=compiled.get_object('snapshot');node_values:=snapshot_value.get_array('nodes');root_value:=treat(node_values.get(0)as json_object_t);
  if snapshot_value.get_number('warehouse')is null or snapshot_value.get_number('warehouse')!=ware_value then raise_application_error(-20886,'SHIPPING_GROSS_WARE_CHANGED');end if;
  if node_values.get_size>200 or snapshot_value.get_array('links').get_size>200 or compiled.get_array('shipments').get_size>200 then raise_application_error(-20881,'SHIPPING_GROSS_CLOSURE_BOUND');end if;
  for i in 0..node_values.get_size-1 loop nodes.append(project_node(treat(node_values.get(i)as json_object_t)));end loop;
  for i in 0..compiled.get_array('shipments').get_size-1 loop
   entry:=treat(compiled.get_array('shipments').get(i)as json_object_t);shipments.append(entry.get_object('domain'));
  end loop;
  projection.put('signature_domain','SHIPPING_GROSS');projection.put('signature_version',1);projection.put('root_uid',identifier_value);
  projection.put('root_version',root_value.get_number('version'));projection.put('warehouse_id',ware_value);projection.put('cell',snapshot_value.get_string('cell'));
  if compiled.has('consolidation_expectations')and not compiled.get('consolidation_expectations').is_null then projection.put('consolidation_expectations',compiled.get('consolidation_expectations'));else projection.put_null('consolidation_expectations');end if;
  projection.put('nodes',sorted(nodes,'NODES'));projection.put('links',sorted(snapshot_value.get_array('links')));projection.put('shipments',sorted(shipments,'SHIPMENTS'));
  -- Opaque native compiler resource keys include current FF/ST anchors; they are NOT invented FF versions.
  projection.put('compiler_references',sorted(json_array_t.parse(r)));wire:=canon(projection).to_clob;
  if dbms_lob.getlength(wire)>131072 then raise_application_error(-20881,'SHIPPING_GROSS_PROJECTION_BOUND');end if;
  result_value.put('signature_domain','SHIPPING_GROSS');result_value.put('signature_version',1);result_value.put('composition_signature',digest(wire));
  result_value.put('projection_json',wire);result_value.put('producer','RRL_SHIPPING_GROSS_READ.freeze');
  result_value.put('frozen_at',to_char(now_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  result_value.put('expires_at',to_char((now_value+interval '120' second)at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  result_value.put('quality_release_approved',false);result_value.put('stock_posted',false);result_value.put('capture_archived',false);
  p_result:=result_value.to_clob;
 end;
end;
/
