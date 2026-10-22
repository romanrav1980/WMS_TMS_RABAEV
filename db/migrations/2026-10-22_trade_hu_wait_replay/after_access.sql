create or replace package body RRL_HU_EXEC_ACCESS as
 procedure assert_pack_replay_owners(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);plan clob;ware number;trade_site number;operation_value varchar2(100);
 begin
  if d.get_string('command_type')not in('HU_ATTACH','HU_DETACH','HU_PLAN_MOVE','HU_TASK_COMPLETE')then return;end if;
  operation_value:=d.get_string('operation_id');
  begin select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION
   where OPERATION_ID=operation_value and STATE='APPLIED'and COMMAND_TYPE in('HU_ATTACH','HU_DETACH','HU_PLAN_MOVE','HU_TASK_COMPLETE');
  exception when no_data_found then return;end;
  select json_value(plan,'$.domain.parent_snapshot.warehouse' returning number)into ware from dual;
  if ware is null or ware<1 then raise_application_error(-20886,'HU_REPLAY_PHYSICAL_WARE_REQUIRED');end if;
  select count(*)into trade_site from RRL_TRADE_SITE where WARE_ID=ware;
  for o in(select a.OWNER_ID,count(*)TOTAL,count(a.PHYSICAL_UNIT_KEY)TAGGED
   from json_table(plan,'$.resources[*]'columns(R number path '$.rank',K varchar2(4000)path '$.key_hex'))j
   left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=lower(substr(utl_raw.cast_to_varchar2(hextoraw(j.K)),-64))
    and rawtohex(RRL_STOCK_LOCK_API.resource_key('UNIT',a.PHYSICAL_UNIT_KEY))=j.K
   where j.R=60 group by a.OWNER_ID)loop
   if o.TAGGED>0 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);end if;
   if trade_site>0 and o.TOTAL<>o.TAGGED then raise_application_error(-20882,'HU_REPLAY_TRADE_ATTRIBUTES_REQUIRED');end if;
  end loop;
 end;
 procedure assert_request(p_request clob,p_actor varchar2)is
  doc json_object_t:=json_object_t.parse(p_request);m json_object_t:=doc.get_object('metadata');
  kind_value varchar2(80):=doc.get_string('command_type');uid_value varchar2(200);cell_value varchar2(60);warehouse_value number;child_value varchar2(200);task_value RRL_WAREHOUSE_TASK%rowtype;case_value number;cell_count number;
  procedure allowed_cell(p_cell varchar2)is w number;
  begin
   select WARE_ID into w from RRL_CELLS where CELL=p_cell;
   if w is null or w<1 or RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(w))!=1 then
    raise_application_error(-20882,'HU_CURRENT_WARE_EXECUTION_FORBIDDEN');end if;
  exception when no_data_found then raise_application_error(-20882,'HU_CURRENT_WARE_EXECUTION_FORBIDDEN');end;
  procedure allowed_container(p_uid varchar2)is c varchar2(60);
  begin
   select case when HU_KIND='CONTAINER'then HU_CURRENT_CELL end into c from RRL_PALLETS where UID_PALLET=p_uid;
   allowed_cell(c);
  exception when no_data_found then raise_application_error(-20882,'HU_CURRENT_WARE_EXECUTION_FORBIDDEN');end;
 begin
  if kind_value not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_MOVE','HU_PLAN_MOVE','HU_TASK_COMPLETE','HU_RELOCATE_SLOT','HU_REPACK_SLOT','HU_UNPACK')then return;end if;
  assert_pack_replay_owners(p_request,p_actor);
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')=1 then return;end if;
  if kind_value='HU_TASK_COMPLETE'and doc.get_object('source').get_number('task_id')is not null then
   warehouse_value:=doc.get_object('source').get_number('task_id');select *into task_value from RRL_WAREHOUSE_TASK where TASK_ID=warehouse_value;
   allowed_cell(task_value.FROM_CELL);allowed_cell(task_value.TO_CELL);return;
  end if;
  uid_value:=doc.get_object('source').get_string('uid');
  if kind_value='HU_RELOCATE_SLOT'then
   case_value:=m.get_number('case_task_id');
   if case_value is not null then
    select WARE_ID into warehouse_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_value;
    if RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(warehouse_value))!=1 then raise_application_error(-20882,'HU_CURRENT_CASE_WARE_EXECUTION_FORBIDDEN');end if;
   else
    select case when HU_KIND='CONTAINER'then HU_CURRENT_CELL end into cell_value from RRL_PALLETS where UID_PALLET=uid_value;
    if cell_value is null then
     select min(CELL),count(distinct CELL)into cell_value,cell_count from RRL_REMAINS where UID_POLETA=uid_value and REMAIN>0;
     if cell_count!=1 then raise_application_error(-20882,'HU_SLOT_CURRENT_STOCK_LOCATION_REQUIRED');end if;
    end if;allowed_cell(cell_value);
   end if;return;
  end if;
  if kind_value='HU_CREATE'then allowed_cell(m.get_string('cell'));
  else
   allowed_container(uid_value);
   if kind_value in('HU_MOVE','HU_PLAN_MOVE','HU_TASK_COMPLETE')then allowed_cell(m.get_string('target_cell'));
   elsif m.get_number('child_case_task_id')is not null then
    case_value:=m.get_number('child_case_task_id');
    select WARE_ID into warehouse_value from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_value;
    if RRL_ACCESS_API.allowed(p_actor,'warehouse_task_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(warehouse_value))!=1 then raise_application_error(-20882,'HU_CURRENT_CASE_WARE_EXECUTION_FORBIDDEN');end if;
   else
    child_value:=m.get_string('child_uid');
    select case when p.HU_KIND='CONTAINER'then p.HU_CURRENT_CELL else
     (select min(r.CELL)from RRL_REMAINS r where r.UID_POLETA=p.UID_PALLET and r.REMAIN>0)end into cell_value
     from RRL_PALLETS p where p.UID_PALLET=child_value;
    allowed_cell(cell_value);
   end if;
  end if;
 exception when no_data_found then raise_application_error(-20882,'HU_CURRENT_WARE_EXECUTION_FORBIDDEN');
 end;
end;
/
