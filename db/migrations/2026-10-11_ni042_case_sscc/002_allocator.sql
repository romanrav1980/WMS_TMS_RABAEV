create or replace package RRL_SSCC_ALLOCATOR authid definer as
 procedure assert_scope(p_ware number,p_actor varchar2,p_permission varchar2);
 function allocate(p_ware number,p_actor varchar2,p_permission varchar2) return varchar2;
end;
/
create or replace package body RRL_SSCC_ALLOCATOR as
 procedure assert_scope(p_ware number,p_actor varchar2,p_permission varchar2)is
  n number;
 begin
  if p_permission not in('case_pick_execute','warehouse_receipt_confirm')or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'SSCC_PERMISSION_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN'or WARE_ID=p_ware);
  if n!=1 then raise_application_error(-20882,'SSCC_CURRENT_WARE_REQUIRED');end if;
 end;
 function allocate(p_ware number,p_actor varchar2,p_permission varchar2)return varchar2 is
  pref varchar2(20);ext number;serial number;width number;body varchar2(17);code varchar2(18);total number:=0;n number;
 begin
  assert_scope(p_ware,p_actor,p_permission);
  select COMPANY_PREFIX,EXTENSION_DIGIT into pref,ext from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;
  if pref is null or not regexp_like(pref,'^[0-9]{6,12}$')or ext is null or ext!=trunc(ext)or ext<0 or ext>9 then raise_application_error(-20887,'ASSIGNED_GS1_PREFIX_REQUIRED');end if;
  select RRL_RECEIPT_SSCC_SQ.nextval into serial from dual;width:=16-length(pref);
  if serial>=power(10,width)then raise_application_error(-20881,'SSCC_SERIAL_RANGE_EXHAUSTED');end if;
  body:=to_char(ext,'FM0')||pref||lpad(to_char(serial,'FM9999999999999990'),width,'0');
  for i in 1..17 loop total:=total+to_number(substr(body,18-i,1))*case when mod(i,2)=1 then 3 else 1 end;end loop;
  code:=body||to_char(mod(10-mod(total,10),10),'FM0');
  select count(*)into n from(select 1 from RRL_PALLETS where UID_PALLET=code or SSCC=code union all
   select 1 from RRL_CASE_PICK_TASK where SSCC=code union all select 1 from RRL_RECEIPT_LABEL where SSCC=code
   union all select 1 from RRL_CASE_SSCC_LABEL where SSCC=code union all select 1 from RRL_SBORKA_PALLETS where PALLET_UID=code)where rownum=1;
  if n>0 then raise_application_error(-20873,'SSCC_ALREADY_EXISTS');end if;
  return code;
 end;
end;
/
