-- Snapshot only planned keys in set SQL; outbox retains only changed unit/reservation rows.
create or replace package RRL_STOCK_CHANGE_AUDIT authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot(p_resources clob) return clob;
 function differences(p_before clob,p_after clob) return clob;
end;
/
create or replace package body RRL_STOCK_CHANGE_AUDIT as
 function parts(p_key raw) return json_array_t is
  result json_array_t:=json_array_t();v_hex varchar2(2000):=rawtohex(p_key);
  pos pls_integer:=1;colon pls_integer;n pls_integer;value varchar2(2000);
 begin
  while pos<=length(v_hex) loop
   colon:=instr(v_hex,'3A',pos);
   while colon>0 and mod(colon,2)=0 loop colon:=instr(v_hex,'3A',colon+1);end loop;
   if colon=0 then raise_application_error(-20841,'AUDIT_RESOURCE_ENCODING_INVALID');end if;
   n:=to_number(utl_i18n.raw_to_char(hextoraw(substr(v_hex,pos,colon-pos)),'AL32UTF8'));
   if n<1 or colon+2+2*n-1>length(v_hex) then raise_application_error(-20841,'AUDIT_RESOURCE_LENGTH_INVALID');end if;
   pos:=colon+2;value:=utl_i18n.raw_to_char(hextoraw(substr(v_hex,pos,2*n)),'AL32UTF8');result.append(value);pos:=pos+2*n;
  end loop;
  if result.get_string(0)!='2' then raise_application_error(-20841,'AUDIT_RESOURCE_VERSION_INVALID');end if;
  return result;
 end;
 function snapshot(p_resources clob) return clob is
  unit_keys json_array_t:=json_array_t();reserve_ids json_array_t:=json_array_t();key_parts json_array_t;
  result json_object_t:=json_object_t();unit_json clob;reserve_json clob;unit_plan clob;reserve_plan clob;key_raw raw(1000);id_text varchar2(100);
 begin
  for r in(select distinct RANK_NO,KEY_HEX from json_table(p_resources,'$[*]' columns(
   RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO in(20,60) order by RANK_NO,KEY_HEX) loop
   key_raw:=hextoraw(r.KEY_HEX);key_parts:=parts(key_raw);
   if r.RANK_NO=60 and key_parts.get_string(1)='UNIT' then
    RRL_STOCK_LOCK_API.assert_held(60,key_raw);unit_keys.append(key_parts.get_string(2));
   elsif r.RANK_NO=20 and key_parts.get_string(1)='ROW' and key_parts.get_string(2)='RRL_STOCK_RESERVATION' then
    RRL_STOCK_LOCK_API.assert_held(20,key_raw);id_text:=key_parts.get_string(3);
    if not regexp_like(id_text,'^[1-9][0-9]*$') then raise_application_error(-20841,'AUDIT_RESERVATION_KEY_INVALID');end if;
    reserve_ids.append(id_text);
   end if;
  end loop;
  if unit_keys.get_size>10000 or reserve_ids.get_size>10000 then raise_application_error(-20881,'AUDIT_CHANGESET_BOUND');end if;
  unit_plan:=unit_keys.to_clob;reserve_plan:=reserve_ids.to_clob;
  select json_arrayagg(json_object(
    'key' value u.PHYSICAL_UNIT_KEY,'origin_uid' value u.UID_PALLET,'unit_id' value u.UNIT_ID,
    'uid' value u.CURRENT_UID,'cell' value u.CURRENT_CELL,'quantity' value to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
    'unit' value u.BASE_UOM,'status' value u.STOCK_STATUS,'version' value u.UNIT_VERSION,'reservation_id' value u.HARD_RESERVATION_ID returning clob)
    order by u.PHYSICAL_UNIT_KEY returning clob) into unit_json
   from RRL_WMS_RECEIPT_UNIT u join json_table(unit_plan,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY;
  select json_arrayagg(json_object(
    'key' value to_char(sr.RESERVATION_ID,'TM9'),'kind' value sr.RESERVATION_KIND,'scope' value sr.RESERVATION_SCOPE,
    'domain' value sr.RESERVATION_DOMAIN,'status' value sr.STATUS,'uid' value sr.UID_PALLET,'cell' value sr.CELL,
    'quantity' value to_char(sr.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),'unit' value sr.BASE_UOM,'version' value sr.RESERVATION_VERSION,
    'owner_type' value sr.SOURCE_DOC_TYPE,'owner_id' value sr.SOURCE_DOC_ID,'owner_line' value sr.SOURCE_LINE_ID,
    'wave_id' value sr.PICK_WAVE_ID,'plan_id' value sr.PICK_PLAN_ID,'plan_line' value sr.PICK_PLAN_LINE_ID,
    'order_id' value sr.CUSTOMER_ORDER_ID,'production_order_id' value sr.PRODUCTION_ORDER_ID,'slot_id' value sr.CELL_SLOT_ID returning clob)
    order by sr.RESERVATION_ID returning clob) into reserve_json
   from RRL_STOCK_RESERVATION sr join json_table(reserve_plan,'$[*]' columns(ID_VALUE number path '$'))j on j.ID_VALUE=sr.RESERVATION_ID;
  result.put('units',json_array_t.parse(nvl(unit_json,to_clob('[]'))));
  result.put('reservations',json_array_t.parse(nvl(reserve_json,to_clob('[]'))));
  return result.to_clob;
 end;
 function differences(p_before clob,p_after clob) return clob is
  before_doc json_object_t:=json_object_t.parse(p_before);after_doc json_object_t:=json_object_t.parse(p_after);result json_object_t:=json_object_t();
  procedure compare_collection(p_name varchar2) is
   old_array json_array_t:=before_doc.get_array(p_name);new_array json_array_t:=after_doc.get_array(p_name);
   changes json_array_t:=json_array_t();old_row json_object_t;new_row json_object_t;change_row json_object_t;k varchar2(200);
   type row_map is table of json_object_t index by varchar2(200);old_rows row_map;new_rows row_map;
  begin
   for i in 0..old_array.get_size-1 loop old_row:=treat(old_array.get(i) as json_object_t);old_rows(old_row.get_string('key')):=old_row;end loop;
   for i in 0..new_array.get_size-1 loop new_row:=treat(new_array.get(i) as json_object_t);new_rows(new_row.get_string('key')):=new_row;end loop;
   k:=old_rows.first;
   while k is not null loop
    old_row:=old_rows(k);change_row:=null;
    if not new_rows.exists(k) then change_row:=json_object_t();change_row.put_null('after');
    elsif dbms_lob.compare(old_row.to_clob,new_rows(k).to_clob)!=0 then change_row:=json_object_t();change_row.put('after',new_rows(k));end if;
    if change_row is not null then change_row.put('key',k);change_row.put('before',old_row);changes.append(change_row);end if;
    k:=old_rows.next(k);
   end loop;
   k:=new_rows.first;
   while k is not null loop
    if not old_rows.exists(k) then change_row:=json_object_t();change_row.put('key',k);change_row.put_null('before');change_row.put('after',new_rows(k));changes.append(change_row);end if;
    k:=new_rows.next(k);
   end loop;
   result.put(p_name,changes);
  end;
 begin
  compare_collection('units');compare_collection('reservations');return result.to_clob;
 end;
end;
/
