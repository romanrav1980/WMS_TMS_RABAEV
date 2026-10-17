create or replace package body RRL_HU_EXEC_ACCESS as
 procedure assert_request(p_request clob,p_actor varchar2)is
  doc json_object_t:=json_object_t.parse(p_request);m json_object_t:=doc.get_object('metadata');
  kind_value varchar2(80):=doc.get_string('command_type');uid_value varchar2(200);cell_value varchar2(60);warehouse_value number;child_value varchar2(200);task_value RRL_WAREHOUSE_TASK%rowtype;case_value number;
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
  if kind_value not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_MOVE','HU_PLAN_MOVE','HU_TASK_COMPLETE')then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')=1 then return;end if;
  if kind_value='HU_TASK_COMPLETE'and doc.get_object('source').get_number('task_id')is not null then
   warehouse_value:=doc.get_object('source').get_number('task_id');select *into task_value from RRL_WAREHOUSE_TASK where TASK_ID=warehouse_value;
   allowed_cell(task_value.FROM_CELL);allowed_cell(task_value.TO_CELL);return;
  end if;
  uid_value:=doc.get_object('source').get_string('uid');
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
