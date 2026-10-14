create or replace package RRL_TRANSPORT_PLAN_RULES authid definer as
 procedure assert_actor(p_actor varchar2,p_ware number);
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob);
end;
/

create or replace package body RRL_TRANSPORT_PLAN_RULES as
 procedure assert_actor(p_actor varchar2,p_ware number)is n number;begin
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'PLAN_CURRENT_WARE_REQUIRED');end if;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
  if n!=1 or p_ware is null then raise_application_error(-20882,'PLAN_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob)is
  v RRL_TR_VEHICLE%rowtype;places number;weight number;unknown_weight number;strict_windows number;bad number;
  result json_object_t:=json_object_t();warn json_array_t:=json_array_t();
 begin
  if p_vehicle_id is null then
   if p_complete=1 then raise_application_error(-20886,'PLAN_CURRENT_VEHICLE_REQUIRED');end if;
   result.put('validation_status','DRAFT_VEHICLE_REQUIRED');warn.append('Машина не назначена; вместимость и сроки не подтверждены');
   result.put('warnings',warn);p_result:=result.to_clob;return;
  end if;
  select *into v from RRL_TR_VEHICLE where ID=p_vehicle_id;
  if nvl(v.BLOCKED,0)!=0 or nvl(v.DELETED,0)!=0 or nvl(v.PALLETS,0)<=0 or nvl(v.MAX_WEIGHT_KG,0)<=0 or v.TR_TYPE is null then raise_application_error(-20886,'PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED');end if;
  select count(distinct p.PALLET_UID),sum(r.ORDER_WEIGHT),
   sum(case when r.ID is null or r.ORDER_WEIGHT is null or r.ORDER_WEIGHT<=0 then 1 else 0 end)
   into places,weight,unknown_weight from RRL_SBORKA_PALLETS p
   left join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')));
  if places>v.PALLETS then raise_application_error(-20886,'PLAN_PALLET_CAPACITY_EXCEEDED');end if;
  if unknown_weight>0 then
   if p_complete=1 then raise_application_error(-20886,'PLAN_DECLARED_WEIGHT_REQUIRED');end if;
   warn.append('Плановая масса части товара отсутствует; окончательная готовность не подтверждена');
  elsif weight>v.MAX_WEIGHT_KG then raise_application_error(-20886,'PLAN_WEIGHT_CAPACITY_EXCEEDED');end if;
  select count(*)into bad from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
   and((a.TRANSPORT_TYPE is not null and trim(a.TRANSPORT_TYPE)not in('0',trim(v.TR_TYPE)))
    or(nvl(a.STOL,0)>0 and nvl(v.GIDROBORT,0)!=1));
  if bad>0 then raise_application_error(-20886,'PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT');end if;
  select count(*)into bad from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
   and a.MAX_VEHICLE_TONS is not null and v.MAX_WEIGHT_KG>1000*a.MAX_VEHICLE_TONS;
  if bad>0 then raise_application_error(-20886,'PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED');end if;
  select count(*)into strict_windows from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))and nvl(a.TW_STRICT,0)=1;
  if strict_windows>0 then
   if p_complete=1 then raise_application_error(-20886,'PLAN_STRICT_TIME_SCHEDULE_REQUIRED');end if;
   warn.append('Жёсткие временные окна требуют подтверждённого расписания');
  end if;
  result.put('validation_status',case when warn.get_size=0 then 'CAPACITY_TYPE_CHECKED'else'DRAFT_INCOMPLETE'end);
  result.put('declared_places',places);result.put('declared_weight_kg',to_char(weight,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));
  result.put('warnings',warn);result.put('physical_stock_changed',false);result.put('physical_load_admission',false);
  p_result:=result.to_clob;
 end;
end;
/
