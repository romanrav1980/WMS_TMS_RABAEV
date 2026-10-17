create or replace package body RRL_HU_THERMAL_READ as
 function admission_json(p_nodes clob,p_ware number,p_cell varchar2,p_more_nodes clob default null)return clob is
  a json_array_t;b json_array_t:=json_array_t();rules json_array_t:=json_array_t();rule_value json_object_t;
  result_value json_object_t:=json_object_t();known_count number:=0;unknown_count number:=0;invalid_count number:=0;sku_count number:=0;
  lo number;hi number;common_lo number;common_hi number;cell_lo number;cell_hi number;cell_ware number;bad_stock number;
  function answer(p_status varchar2,p_allowed boolean,p_code varchar2)return clob is begin
   result_value.put('domain','HU_THERMAL_ADMISSION');result_value.put('version',1);
   result_value.put('warehouse_id',p_ware);result_value.put('cell',p_cell);result_value.put('status',p_status);result_value.put('allowed',p_allowed);result_value.put('code',p_code);
   result_value.put('policy_only',true);result_value.put_null('observed_temperature_c');result_value.put('source','RRL_RECEIPT_SKU_RULE/RRL_RECEIPT_CELL_RULE');
   result_value.put('known_sku_count',known_count);result_value.put('unknown_sku_count',unknown_count);result_value.put('sku_count',sku_count);
   if common_lo is null then result_value.put_null('common_min_c');else result_value.put('common_min_c',common_lo);end if;
   if common_hi is null then result_value.put_null('common_max_c');else result_value.put('common_max_c',common_hi);end if;
   if cell_lo is null then result_value.put_null('cell_min_c');else result_value.put('cell_min_c',cell_lo);end if;
   if cell_hi is null then result_value.put_null('cell_max_c');else result_value.put('cell_max_c',cell_hi);end if;
   result_value.put('rules',rules);return result_value.to_clob;
  end;
 begin
  if p_nodes is null or dbms_lob.getlength(p_nodes)>2097152 or(p_more_nodes is not null and dbms_lob.getlength(p_more_nodes)>2097152)then raise_application_error(-20881,'HU_THERMAL_INPUT_BOUND');end if;
  a:=json_array_t.parse(p_nodes);if p_more_nodes is not null then b:=json_array_t.parse(p_more_nodes);end if;
  if a.get_size+b.get_size>200 then raise_application_error(-20881,'HU_THERMAL_NODE_BOUND_200');end if;
  if p_ware is null or p_ware<1 or p_cell is null then return answer('INVALID_LOCATION',false,'HU_THERMAL_LOCATION_REQUIRED');end if;
  begin select WARE_ID into cell_ware from RRL_CELLS where CELL=p_cell;
  exception when no_data_found then return answer('INVALID_LOCATION',false,'HU_THERMAL_CELL_NOT_FOUND');end;
  if cell_ware is null or cell_ware!=p_ware then return answer('INVALID_LOCATION',false,'HU_THERMAL_CELL_WAREHOUSE_MISMATCH');end if;
  select count(*)into bad_stock from(
   select KIND,ARTICLE from json_table(p_nodes,'$[*]'columns(KIND varchar2(20)path '$.kind',ARTICLE varchar2(160)path '$.article'))
   union all select KIND,ARTICLE from json_table(p_more_nodes,'$[*]'columns(KIND varchar2(20)path '$.kind',ARTICLE varchar2(160)path '$.article')))
   where KIND='STOCK'and ARTICLE is null;
  if bad_stock!=0 then return answer('INVALID_SOURCE',false,'HU_THERMAL_STOCK_ARTICLE_REQUIRED');end if;
  for sku in(select ARTICLE from(select distinct ARTICLE from(
   select ARTICLE from json_table(p_nodes,'$[*]'columns(ARTICLE varchar2(160)path '$.article'))
   union all select ARTICLE from json_table(p_more_nodes,'$[*]'columns(ARTICLE varchar2(160)path '$.article')))
   where ARTICLE is not null)order by nlssort(ARTICLE,'NLS_SORT=BINARY'))loop
   sku_count:=sku_count+1;lo:=null;hi:=null;
   begin select TEMP_MIN,TEMP_MAX into lo,hi from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=sku.ARTICLE;
   exception when no_data_found then null;end;
   rule_value:=json_object_t();rule_value.put('article',sku.ARTICLE);
   if lo is null then rule_value.put_null('min_c');else rule_value.put('min_c',lo);end if;
   if hi is null then rule_value.put_null('max_c');else rule_value.put('max_c',hi);end if;rules.append(rule_value);
   if lo is null and hi is null then unknown_count:=unknown_count+1;
   elsif lo is null or hi is null or lo>hi then invalid_count:=invalid_count+1;
   else
    known_count:=known_count+1;
    if common_lo is null or lo>common_lo then common_lo:=lo;end if;
    if common_hi is null or hi<common_hi then common_hi:=hi;end if;
   end if;
  end loop;
  if sku_count=0 then return answer('EMPTY',true,'HU_THERMAL_NO_STOCK');end if;
  if invalid_count>0 then return answer('INVALID_POLICY',false,'HU_THERMAL_SKU_POLICY_INVALID');end if;
  if known_count=0 then return answer('UNSPECIFIED',true,'HU_THERMAL_RULES_UNSPECIFIED');end if;
  if unknown_count>0 then return answer('INCOMPLETE_POLICY',false,'HU_THERMAL_ALL_SKU_RULES_REQUIRED');end if;
  if common_lo>common_hi then return answer('DISJOINT',false,'HU_THERMAL_PRODUCT_RANGES_DISJOINT');end if;
  begin select TEMP_MIN,TEMP_MAX into cell_lo,cell_hi from RRL_RECEIPT_CELL_RULE where WARE_ID=p_ware and CELL=p_cell;
  exception when no_data_found then null;end;
  if cell_lo is null or cell_hi is null then return answer('TARGET_POLICY_MISSING',false,'HU_THERMAL_TARGET_RULE_REQUIRED');end if;
  if cell_lo>cell_hi or cell_lo<common_lo or cell_hi>common_hi then return answer('TARGET_INCOMPATIBLE',false,'HU_THERMAL_TARGET_RANGE_INCOMPATIBLE');end if;
  return answer('ADMISSIBLE',true,'HU_THERMAL_POLICY_ADMISSIBLE');
 end;
 procedure assert_admission(p_admission clob,p_require_known number default 0)is j json_object_t:=json_object_t.parse(p_admission);mode_value json_object_t:=json_object_t();begin
  if j.get_string('domain')!='HU_THERMAL_ADMISSION'or j.get_number('version')!=1 or j.get('allowed').is_null then raise_application_error(-20886,'HU_THERMAL_NATIVE_ADMISSION_REQUIRED');end if;
  if not j.get_boolean('allowed')then raise_application_error(-20886,j.get_string('code'));end if;
  if p_require_known=1 and j.get_string('status')='UNSPECIFIED'then raise_application_error(-20886,'HU_THERMAL_KNOWN_POLICY_REQUIRED');end if;
  if j.get_string('status')='ADMISSIBLE'then
   mode_value.put('task_temp_min',j.get_number('common_min_c'));mode_value.put('task_temp_max',j.get_number('common_max_c'));
   RRL_INTERWARE_THERMAL.assert_cell(mode_value.to_clob,j.get_number('warehouse_id'),j.get_string('cell'));
  end if;
 end;
 procedure assert_current(p_expected clob,p_nodes clob,p_ware number,p_cell varchar2,p_more_nodes clob default null)is current_value clob;begin
  current_value:=admission_json(p_nodes,p_ware,p_cell,p_more_nodes);assert_admission(current_value);
  if p_expected is null or dbms_lob.compare(current_value,p_expected)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: HU thermal policy');end if;
 end;
end;
/
