create or replace package RRL_STOCK_EVENT_BRIDGE authid definer
 accessible by(trigger "BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0") as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number);
end;
/
create or replace package body RRL_STOCK_EVENT_BRIDGE as
 procedure after_event(p_operation varchar2,p_line number,p_leg number,p_uid varchar2,p_from varchar2,p_to varchar2,
  p_qty number,p_uom varchar2,p_uom_version number,p_type number) is
  setting varchar2(20);req clob;d json_object_t;a json_array_t;l json_object_t;found boolean:=false;
  base varchar2(20);num number;den number;scale number;ver number;qty number;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','MODE')='EXPLICIT' then return;end if;
  select nvl(max(SETTING_VALUE),'0') into setting from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
  if setting!='1' then raise_application_error(-20863,'LEGACY_STOCK_POSTING_DISABLED');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='COMPAT'
   or p_operation is null or p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'LEGACY_PLAN_REQUIRED');end if;
  select CANONICAL_REQUEST into req from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and COMMAND_TYPE='COMPAT_MANUAL_MOVE' and STATE='IN_FLIGHT';
  d:=json_object_t.parse(req);a:=d.get_array('lines');
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);
   if l.get_number('line_number')=p_line then
    if found then raise_application_error(-20870,'LEGACY_MANIFEST_LINE_REPEATED');end if;found:=true;
    declare
 v_json_sql_1_1 varchar2(32767):=l.get_string('article');
 v_json_sql_1_2 varchar2(32767):=l.get_string('unit');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_1_1 and INPUT_UOM=v_json_sql_1_2;
end;
    declare
 v_json_sql_2_1 varchar2(32767):=l.get_string('article');
 v_json_sql_2_2 varchar2(32767):=l.get_string('unit');
begin
select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into base,num,den,scale from RRL_STOCK_UOM_CONVERSION
     where ARTICUL=v_json_sql_2_1 and INPUT_UOM=v_json_sql_2_2 and POLICY_VERSION=ver;
end;
    qty:=RRL_STOCK_MATH.convert_exact(l.get_string('quantity'),num,den,scale);
    declare
 v_json_sql_3_1 varchar2(32767):=l.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_3_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
    if p_leg!=1 or p_type!=2 or p_from is null or p_to is null or p_from!=l.get_string('source_cell') or p_to!=l.get_string('target_cell')
     or p_uid!=l.get_string('uid') or p_qty!=qty or p_uom!=base or p_uom_version!=ver then raise_application_error(-20870,'LEGACY_MANIFEST_EVENT_CONFLICT');end if;
   end if;
  end loop;
  if not found then raise_application_error(-20870,'LEGACY_MANIFEST_LINE_REQUIRED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_from,-p_qty,0,p_uom,p_uom_version);
  RRL_STOCK_BALANCE_CORE.apply_delta(p_uid,p_to,p_qty,0,p_uom,p_uom_version);
 end;
end;
/
