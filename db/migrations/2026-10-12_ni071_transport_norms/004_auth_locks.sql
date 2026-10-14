create or replace package RRL_TRANSPORT_NORM_API authid definer as
 procedure publish(p_request clob,p_actor varchar2,p_result out clob);
 function writing return boolean;
end;
/
create or replace package body RRL_TRANSPORT_NORM_API as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 function decimal_value(d json_object_t,k varchar2)return number is v varchar2(100):=d.get_string(k);begin
  if v is null or not regexp_like(v,'^[0-9]{1,18}([.][0-9]{1,9})?$')then raise_application_error(-20886,'TRANSPORT_NORM_EXACT_RATE_REQUIRED');end if;
  return to_number(v,'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
 end;
 procedure publish(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);source json_object_t:=json_object_t();result json_object_t:=json_object_t();
 op varchar2(100):=d.get_string('operation_id');price_id number:=d.get_number('source_price_id');ware number:=d.get_number('warehouse_id');
 version number:=d.get_number('expected_version');n number;current_version number;head_ware number;user_group_name varchar2(255);effective date;last_date date;region varchar2(64);tz_check varchar2(64);
 currency_value varchar2(3);vehicle_type varchar2(40);size_class varchar2(40);old_actor nvarchar2(50);old_request clob;source_body clob;price RRL_TRANSPORT_PRICE%rowtype;
 roll_rate number;manual_rate number;loader_rate number;keys json_key_list:=d.get_keys;k varchar2(100);
 begin
  savepoint transport_norm_publish;
  if op is null or length(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')or
    price_id is null or price_id<1 or price_id!=trunc(price_id)or ware is null or ware<1 or
    version is null or version<0 or version!=trunc(version)then raise_application_error(-20886,'TRANSPORT_NORM_INPUT_REQUIRED');end if;
  if keys.count!=14 then raise_application_error(-20886,'TRANSPORT_NORM_FIELDS_REQUIRED');end if;
  for i in 1..keys.count loop k:=keys(i);
   if k not in('operation_id','source_price_id','warehouse_id','currency','effective_from','timezone_region','vehicle_type','vehicle_size_class',
    'rolling_unload_rate','manual_unload_rate','loader_rate','expected_version','reason','decision_reference')then raise_application_error(-20886,'TRANSPORT_NORM_UNKNOWN_FIELD');end if;
  end loop;
  -- Stable current actor/group/grant during row waits and saved-result replay.
  begin
   select USER_GROUP into user_group_name from RUSERS where ID=p_actor and nvl(DELETED,0)=0 for update;
  exception when no_data_found then raise_application_error(-20882,'TRANSPORT_NORM_CURRENT_FINANCE_REQUIRED');end;
  if upper(trim(user_group_name))!='GLOBAL_ADMIN'then
   n:=0;
   for grant_row in(select ID from RIGHTS where USER_GROUP=user_group_name and upper(trim(RIGHT1))='CREATE_TT_PRICE'order by ID for update)loop n:=n+1;end loop;
   if n=0 then raise_application_error(-20882,'TRANSPORT_NORM_CURRENT_FINANCE_REQUIRED');end if;
  end if;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and
   (u.WARE_ID=ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(p_actor,'create_tt_price')=1
   and 1=(select count(*)from RRL_WARES where ID=ware);
  if n!=1 then raise_application_error(-20882,'TRANSPORT_NORM_CURRENT_FINANCE_REQUIRED');end if;
  begin
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_TRANSPORT_NORM_HISTORY where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'TRANSPORT_NORM_OPERATION_CONFLICT');end if;
   return;
  exception when no_data_found then null;end;
  currency_value:=d.get_string('currency');region:=d.get_string('timezone_region');vehicle_type:=d.get_string('vehicle_type');size_class:=d.get_string('vehicle_size_class');
  if currency_value is null or not regexp_like(currency_value,'^[A-Z]{3}$')or region is null or
   vehicle_type is null or size_class is null or length(size_class)>40 or
   trim(d.get_string('reason'))is null or lengthb(d.get_string('reason'))>1000 or
   trim(d.get_string('decision_reference'))is null or lengthb(d.get_string('decision_reference'))>255
   then raise_application_error(-20886,'TRANSPORT_NORM_CONTRACT_REQUIRED');end if;
  select to_char(systimestamp at time zone(region),'TZR')into tz_check from dual;
  effective:=to_date(d.get_string('effective_from'),'FXYYYY-MM-DD');
  select count(*)into n from RRL_TRANSPORT_TYPE where TRANSPORTTYPE=vehicle_type;
  if n!=1 then raise_application_error(-20886,'TRANSPORT_NORM_VEHICLE_TYPE_REQUIRED');end if;
  roll_rate:=decimal_value(d,'rolling_unload_rate');manual_rate:=decimal_value(d,'manual_unload_rate');loader_rate:=decimal_value(d,'loader_rate');
  -- Original rate row serialises publications and prevents a concurrent legacy edit.
  begin select *into price from RRL_TRANSPORT_PRICE where ID=price_id for update;
  exception when no_data_found then raise_application_error(-20886,'TRANSPORT_NORM_LEGACY_SOURCE_REQUIRED');end;
  -- Same-op sender may have waited for another transaction to commit.
  begin
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_TRANSPORT_NORM_HISTORY where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'TRANSPORT_NORM_OPERATION_CONFLICT');end if;
   return;
  exception when no_data_found then null;end;
  if price.PRICE is null or price.PRICE<0 or price.PRICE_FOR_HOURS is null or price.PRICE_FOR_HOURS<0 or
   price.PRICE_FOR_ADDR is null or price.PRICE_FOR_ADDR<0 or price.PRICE>=1e18 or price.PRICE_FOR_HOURS>=1e18 or price.PRICE_FOR_ADDR>=1e18 or
   price.PRICE*1e9!=trunc(price.PRICE*1e9)or price.PRICE_FOR_HOURS*1e9!=trunc(price.PRICE_FOR_HOURS*1e9)or
   price.PRICE_FOR_ADDR*1e9!=trunc(price.PRICE_FOR_ADDR*1e9)or price.PRICE_NAME is null or price.COMPANY is null
   then raise_application_error(-20886,'TRANSPORT_NORM_LEGACY_SOURCE_INCOMPLETE');end if;
  if (price.TYPE_TR is not null and price.TYPE_TR!=vehicle_type)or
   substr(price.PRICE_NAME,1,length(vehicle_type)+2)!='['||vehicle_type||']'
   then raise_application_error(-20886,'TRANSPORT_NORM_LEGACY_TYPE_MISMATCH');end if;
  g_writing:=true;
  merge into RRL_TRANSPORT_NORM_HEAD h using(select price_id P,ware W from dual)s on(h.SOURCE_PRICE_ID=s.P)
   when not matched then insert(SOURCE_PRICE_ID,WARE_ID,VERSION_NO)values(s.P,s.W,0);
  select VERSION_NO,WARE_ID into current_version,head_ware from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=price_id for update;
  if head_ware!=ware then raise_application_error(-20882,'TRANSPORT_NORM_SOURCE_WAREHOUSE_CONFLICT');end if;
  if current_version!=version then raise_application_error(-20867,'TRANSPORT_NORM_VERSION_CONFLICT');end if;
  select max(EFFECTIVE_FROM)into last_date from RRL_TRANSPORT_NORM_HISTORY where SOURCE_PRICE_ID=price_id;
  if effective<last_date then raise_application_error(-20886,'TRANSPORT_NORM_BACKDATED_REVISION_REFUSED');end if;
  source.put('id',price.ID);source.put('price_name',price.PRICE_NAME);source.put('company',price.COMPANY);source.put('vehicle_type',vehicle_type);
  source.put('vehicle_rate',RRL_STOCK_PLAN_HELPER.decimal_text(price.PRICE));source.put('hour_rate',RRL_STOCK_PLAN_HELPER.decimal_text(price.PRICE_FOR_HOURS));
  source.put('point_rate',RRL_STOCK_PLAN_HELPER.decimal_text(price.PRICE_FOR_ADDR));source.put('norm_hours',RRL_STOCK_PLAN_HELPER.decimal_text(price.NORM_HOURS));
  result.put('operation_id',op);result.put('source_price_id',price_id);result.put('warehouse_id',ware);result.put('version',version+1);
  result.put('currency',currency_value);result.put('effective_from',to_char(effective,'YYYY-MM-DD'));result.put('timezone_region',region);
  result.put('vehicle_type',vehicle_type);result.put('vehicle_size_class',size_class);result.put('source',source);
  result.put('rolling_unload_rate',RRL_STOCK_PLAN_HELPER.decimal_text(roll_rate));result.put('manual_unload_rate',RRL_STOCK_PLAN_HELPER.decimal_text(manual_rate));
  result.put('loader_rate',RRL_STOCK_PLAN_HELPER.decimal_text(loader_rate));result.put('status','PUBLISHED');
  result.put('carrier_price_changed',false);result.put('stock_changed',false);result.put('cost_posted',false);
  p_result:=result.to_clob;source_body:=source.to_clob;
  update RRL_TRANSPORT_NORM_HEAD set VERSION_NO=version+1 where SOURCE_PRICE_ID=price_id;
  insert into RRL_TRANSPORT_NORM_HISTORY(SOURCE_PRICE_ID,VERSION_NO,OPERATION_ID,WARE_ID,ACTOR,EFFECTIVE_FROM,CURRENCY,TIME_ZONE,VEHICLE_TYPE,VEHICLE_SIZE_CLASS,REQUEST_JSON,SOURCE_JSON,RESULT_JSON)
  values(price_id,version+1,op,ware,p_actor,effective,currency_value,region,vehicle_type,size_class,p_request,source_body,p_result);
  g_writing:=false;
 exception
  when dup_val_on_index then
   g_writing:=false;rollback to transport_norm_publish;
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_TRANSPORT_NORM_HISTORY where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'TRANSPORT_NORM_OPERATION_CONFLICT');end if;
  when too_many_rows then g_writing:=false;rollback to transport_norm_publish;raise_application_error(-20886,'TRANSPORT_NORM_LEGACY_SOURCE_AMBIGUOUS');
  when others then g_writing:=false;rollback to transport_norm_publish;raise;
 end;
end;
/
create or replace trigger RRL_TRANSPORT_NORM_HEAD_G before insert or update or delete on RRL_TRANSPORT_NORM_HEAD for each row
begin
 if deleting or not RRL_TRANSPORT_NORM_API.writing then raise_application_error(-20863,'TRANSPORT_NORM_PUBLISHED_OWNER_REQUIRED');end if;
 if inserting and :new.VERSION_NO!=0 then raise_application_error(-20863,'TRANSPORT_NORM_INITIAL_VERSION_REQUIRED');end if;
 if updating and(:new.SOURCE_PRICE_ID!=:old.SOURCE_PRICE_ID or :new.WARE_ID!=:old.WARE_ID or :new.VERSION_NO!=:old.VERSION_NO+1)
 then raise_application_error(-20863,'TRANSPORT_NORM_VERSION_HISTORY_REQUIRED');end if;
end;
/
create or replace trigger RRL_TRANSPORT_NORM_HIST_G before insert or update or delete on RRL_TRANSPORT_NORM_HISTORY for each row
declare n number;
begin
 if not inserting or not RRL_TRANSPORT_NORM_API.writing then raise_application_error(-20863,'TRANSPORT_NORM_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_TRANSPORT_NORM_HEAD where SOURCE_PRICE_ID=:new.SOURCE_PRICE_ID and VERSION_NO=:new.VERSION_NO and WARE_ID=:new.WARE_ID;
 if n!=1 then raise_application_error(-20863,'TRANSPORT_NORM_PUBLISHED_VERSION_REQUIRED');end if;
end;
/
