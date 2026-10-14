create or replace package RRL_FORECAST_PROJECTOR authid definer as
 function load_write_allowed(p_load varchar2)return number;
 function day_write_allowed(p_ware number,p_day date)return number;
 procedure project_load(p_load varchar2,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_FORECAST_PROJECTOR as
 g_load varchar2(100);g_tx varchar2(100);g_ware number;g_day date;
 procedure reset_context is begin g_load:=null;g_tx:=null;g_ware:=null;g_day:=null;end;
 function load_write_allowed(p_load varchar2)return number is begin
  if g_load=p_load and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;end;
 function day_write_allowed(p_ware number,p_day date)return number is begin
  if g_ware=p_ware and g_day=p_day and g_load is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;end;
 procedure increment_day is begin
  update RRL_FORECAST_DAY set LOAD_COUNT=LOAD_COUNT+1,TOP_PLACES=TOP_PLACES+1,LAST_LOAD_OPERATION=g_load where WARE_ID=g_ware and DAY_UTC=g_day;
  if sql%rowcount=0 then
   begin insert into RRL_FORECAST_DAY values(g_ware,g_day,1,1,g_load);
   exception when dup_val_on_index then update RRL_FORECAST_DAY set LOAD_COUNT=LOAD_COUNT+1,TOP_PLACES=TOP_PLACES+1,LAST_LOAD_OPERATION=g_load where WARE_ID=g_ware and DAY_UTC=g_day;end;
  end if;
 end;
 procedure increment_sku(p_article varchar2,p_base varchar2,p_kind varchar2,p_qty number,p_leaves number)is begin
  update RRL_FORECAST_SKU_DAY set BASE_QTY=BASE_QTY+p_qty,LEAF_COUNT=LEAF_COUNT+p_leaves,SOURCE_COUNT=SOURCE_COUNT+1 where WARE_ID=g_ware and DAY_UTC=g_day and ARTICLE=p_article and BASE_UOM=p_base and WORK_KIND=p_kind;
  if sql%rowcount=0 then
   begin insert into RRL_FORECAST_SKU_DAY values(g_ware,g_day,p_article,p_base,p_kind,p_qty,p_leaves,1);
   exception when dup_val_on_index then
    update RRL_FORECAST_SKU_DAY set BASE_QTY=BASE_QTY+p_qty,LEAF_COUNT=LEAF_COUNT+p_leaves,SOURCE_COUNT=SOURCE_COUNT+1 where WARE_ID=g_ware and DAY_UTC=g_day and ARTICLE=p_article and BASE_UOM=p_base and WORK_KIND=p_kind;
   end;
  end if;
 end;
 procedure project_load(p_load varchar2,p_actor varchar2,p_result out clob)is
  source_row RRL_TT_HU_LOAD_FACT%rowtype;raw_hash varchar2(64);old_hash varchar2(64);old_result clob;leaves clob;
  lines json_array_t;node json_object_t;result json_object_t:=json_object_t();qty number;uid varchar2(200);article varchar2(160);base varchar2(20);kind varchar2(20);case_id number;allowed number;
  type group_record is record(article varchar2(160),base varchar2(20),kind varchar2(20),qty number,leaves number);
  type group_map is table of group_record index by varchar2(500);groups group_map;key_text varchar2(500);
  leaf_total number;old_ware number;old_article varchar2(160);old_base varchar2(20);
 begin
  reset_context;
  select *into source_row from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  if source_row.STATUS!='DEPARTED'or source_row.DEPARTED_AT is null then raise_application_error(-20886,'FORECAST_DEPARTED_SOURCE_REQUIRED');end if;
  select count(*)into allowed from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=source_row.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
  if allowed!=1 then raise_application_error(-20882,'FORECAST_CURRENT_WARE_ACTOR_REQUIRED');end if;
  raw_hash:=lower(rawtohex(sys.dbms_crypto.hash(source_row.COMPOSITION_JSON,sys.dbms_crypto.hash_sh256)));
  begin select SOURCE_HASH,RESULT_JSON into old_hash,old_result from RRL_FORECAST_LOAD where LOAD_OPERATION_ID=p_load;
   if old_hash!=raw_hash then raise_application_error(-20886,'FORECAST_SOURCE_HASH_CHANGED');end if;p_result:=old_result;return;
  exception when no_data_found then null;end;
  RRL_FORECAST_SOURCE_RULES.compile_leaves(source_row.COMPOSITION_JSON,source_row.WARE_ID,leaves);lines:=json_array_t.parse(leaves);leaf_total:=lines.get_size;
  g_load:=p_load;g_ware:=source_row.WARE_ID;g_tx:=dbms_transaction.local_transaction_id(true);
  select trunc(cast(source_row.DEPARTED_AT at time zone 'UTC'as date))into g_day from dual;
  result.put('source_load_operation_id',p_load);result.put('warehouse_id',g_ware);result.put('source_hash',raw_hash);
  result.put('leaf_count',lines.get_size);result.put('top_places',1);result.put('day_utc',to_char(g_day,'YYYY-MM-DD'));
  result.put('stock_changed',false);result.put('status','PROJECTED');p_result:=result.to_clob;
  begin
   insert into RRL_FORECAST_LOAD(LOAD_OPERATION_ID,WARE_ID,DAY_UTC,DEPARTED_AT,SOURCE_HASH,LEAF_COUNT,TOP_PLACES,PROJECTED_BY,RESULT_JSON)
    values(p_load,g_ware,g_day,source_row.DEPARTED_AT,raw_hash,leaf_total,1,p_actor,p_result);
  exception when dup_val_on_index then
   select SOURCE_HASH,RESULT_JSON into old_hash,old_result from RRL_FORECAST_LOAD where LOAD_OPERATION_ID=p_load;
   if old_hash!=raw_hash then raise_application_error(-20886,'FORECAST_SOURCE_HASH_CHANGED');end if;p_result:=old_result;reset_context;return;
  end;
  -- compile_leaves returns stable CASE-origin/UID order; no warehouse-stock locks.
  for i in 0..lines.get_size-1 loop
   node:=treat(lines.get(i)as json_object_t);uid:=node.get_string('uid');article:=node.get_string('article');base:=node.get_string('base_uom');kind:=node.get_string('work_kind');case_id:=node.get_number('case_task_id');qty:=RRL_STOCK_MATH.quantity(node.get_string('quantity'));
   if kind='CASE_DISPATCH'then
    begin insert into RRL_FORECAST_CASE_ORIGIN values(case_id,uid,p_load,g_ware,article,base,qty);
    exception when dup_val_on_index then
     select WARE_ID,ARTICLE,BASE_UOM into old_ware,old_article,old_base from RRL_FORECAST_CASE_ORIGIN where CASE_PICK_TASK_ID=case_id and LOT_UID=uid;
     if old_ware!=g_ware or old_article!=article or old_base!=base then raise_application_error(-20886,'FORECAST_CASE_ORIGIN_CONFLICT');end if;
     kind:='CASE_RELOADED';
    end;
   end if;
   insert into RRL_FORECAST_LEAF values(p_load,i+1,uid,article,base,qty,kind,case_id);
   key_text:=kind||':'||lengthb(article)||':'||article||':'||lengthb(base)||':'||base;
   if not groups.exists(key_text)then groups(key_text).article:=article;groups(key_text).base:=base;groups(key_text).kind:=kind;groups(key_text).qty:=0;groups(key_text).leaves:=0;end if;
   groups(key_text).qty:=groups(key_text).qty+qty;groups(key_text).leaves:=groups(key_text).leaves+1;
  end loop;
  increment_day;key_text:=groups.first;
  while key_text is not null loop
   increment_sku(groups(key_text).article,groups(key_text).base,groups(key_text).kind,groups(key_text).qty,groups(key_text).leaves);key_text:=groups.next(key_text);
  end loop;
  reset_context;
 exception when others then reset_context;raise;
 end;
end;
/
