create or replace package body RRL_INVENTORY_TASK_ACCESS as
 function legacy_home(p_actor varchar2,p_warehouse number)return number is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and(WARE_ID=p_warehouse or upper(trim(USER_GROUP))='GLOBAL_ADMIN');return least(n,1);
 end;
 procedure active_actor(p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'INVENTORY_CURRENT_ACTIVE_ACTOR_REQUIRED');end if;
 end;
 procedure legacy_warehouse(p_actor varchar2,p_warehouse number)is n number;begin
  active_actor(p_actor);
  select count(*)into n from RUSERS where ID=p_actor and(WARE_ID=p_warehouse or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INVENTORY_CURRENT_WAREHOUSE_ACTOR_REQUIRED');end if;
 end;
 procedure task_authority(p_task number,p_actor varchar2,p_action varchar2,p_operation varchar2 default null)is
  t RRL_INVENTORY_TASK%rowtype;cell_ware number;
 begin
  active_actor(p_actor);
  if p_task is null or p_task<1 or p_task!=trunc(p_task)then raise_application_error(-20886,'INVENTORY_TASK_ID_REQUIRED');end if;
  select *into t from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=p_task;
  if t.WARE_ID is null or t.CELL_CODE is null or t.ARTICUL is null then raise_application_error(-20886,'INVENTORY_TASK_SOURCE_IDENTITY_REQUIRED');end if;
  select WARE_ID into cell_ware from RRL_CELLS where CELL=t.CELL_CODE;
  if cell_ware is null or cell_ware!=t.WARE_ID then raise_application_error(-20886,'INVENTORY_TASK_CELL_WARE_CHANGED');end if;
  if RRL_ACCESS_API.allowed(p_actor,'inventory_task_execute','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(t.WARE_ID),t.ASSIGNED_TO)!=1
   or RRL_ACCESS_API.allowed(p_actor,'stock_inventory_count','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(t.WARE_ID),t.ASSIGNED_TO)!=1 then
   raise_application_error(-20882,'INVENTORY_CURRENT_TASK_SCOPE_REQUIRED');end if;
  if p_action='CLAIM'then
   if t.STATUS is null or t.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')or(t.ASSIGNED_TO is not null and t.ASSIGNED_TO!=p_actor)then
    raise_application_error(-20886,'INVENTORY_TASK_CLAIM_STATE_CONFLICT');end if;
  elsif p_action='COUNT'then
   if t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'INVENTORY_CURRENT_ASSIGNED_AUDITOR_REQUIRED');end if;
   if t.STATUS='DONE'then
    if p_operation is null or t.COUNT_OPERATION_ID is null or t.COUNT_OPERATION_ID!=p_operation then raise_application_error(-20886,'INVENTORY_TASK_ALREADY_COUNTED');end if;
   elsif t.STATUS is null or t.STATUS!='IN_PROGRESS'then raise_application_error(-20886,'INVENTORY_TASK_CLAIM_BEFORE_COUNT_REQUIRED');end if;
  elsif p_action='READ'then
   if t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'INVENTORY_CURRENT_ASSIGNED_AUDITOR_REQUIRED');end if;
  else raise_application_error(-20886,'INVENTORY_TASK_ACTION_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20884,'INVENTORY_TASK_SOURCE_NOT_FOUND');end;
 procedure assert_task_count(p_task number,p_actor varchar2,p_operation varchar2,p_revision number)is
  t RRL_INVENTORY_TASK%rowtype;ware number;
 begin
  task_authority(p_task,p_actor,'COUNT',p_operation);
  select *into t from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=p_task;
  select WARE_ID into ware from RRL_REVIZION where ID=p_revision;
  if ware is null or ware!=t.WARE_ID then raise_application_error(-20882,'INVENTORY_TASK_REVISION_SCOPE_CONFLICT');end if;
 end;
 procedure assert_count(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;task_no number;ware number;doc number;
  t RRL_INVENTORY_TASK%rowtype;counts json_array_t;item json_object_t;legacy_count boolean;
 begin
  active_actor(p_actor);m:=d.get_object('metadata');doc:=d.get_object('source').get_number('revision_id');
  select WARE_ID into ware from RRL_REVIZION where ID=doc;
  legacy_count:=RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')=1 and legacy_home(p_actor,ware)=1;
  if legacy_count then
   legacy_warehouse(p_actor,ware);
   -- The old standalone count and old flat task actor keep their original policy.
   if not m.has('inventory_task_id')or m.get('inventory_task_id').is_null or RRL_HAS_WRIGHT(p_actor,'inventory_task_execute')=1 then return;end if;
  end if;
  if not m.has('inventory_task_id')or m.get('inventory_task_id').is_null then raise_application_error(-20882,'INVENTORY_SCOPED_TASK_BINDING_REQUIRED');end if;
  task_no:=m.get_number('inventory_task_id');assert_task_count(task_no,p_actor,d.get_string('operation_id'),doc);
  select *into t from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=task_no;
  counts:=m.get_array('counts');
  if counts is null or counts.get_size>200 or m.has('revision_row_id')then raise_application_error(-20886,'INVENTORY_TASK_COUNT_SCOPE_REQUIRED');end if;
  for i in 0..counts.get_size-1 loop
   item:=treat(counts.get(i)as json_object_t);
   if item.get_string('cell')is null or item.get_string('cell')!=t.CELL_CODE or item.get_string('article')is null or item.get_string('article')!=t.ARTICUL then
    raise_application_error(-20882,'INVENTORY_TASK_COUNT_CELL_ARTICLE_FORBIDDEN');end if;
  end loop;
 exception when no_data_found then raise_application_error(-20884,'INVENTORY_COUNT_SOURCE_NOT_FOUND');end;
 procedure assert_read(p_actor varchar2,p_revision number,p_warehouse number,p_task number default null,p_cell varchar2 default null,p_article varchar2 default null)is
  ware number;cell_ware number;t RRL_INVENTORY_TASK%rowtype;
 begin
  active_actor(p_actor);
  if p_revision is not null then select WARE_ID into ware from RRL_REVIZION where ID=p_revision;else ware:=p_warehouse;end if;
  if ware is null or ware<1 then raise_application_error(-20882,'INVENTORY_READ_WAREHOUSE_REQUIRED');end if;
  if p_cell is not null then
   select WARE_ID into cell_ware from RRL_CELLS where CELL=p_cell;
   if cell_ware is null or cell_ware!=ware then raise_application_error(-20882,'INVENTORY_READ_CELL_WAREHOUSE_FORBIDDEN');end if;
  end if;
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')=1 and legacy_home(p_actor,ware)=1 then return;end if;
  if p_task is not null then
   task_authority(p_task,p_actor,'READ');select *into t from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=p_task;
   if t.WARE_ID!=ware then raise_application_error(-20882,'INVENTORY_TASK_READ_WAREHOUSE_FORBIDDEN');end if;
   if p_cell is not null and(p_cell!=t.CELL_CODE or p_article is null or p_article!=t.ARTICUL)then raise_application_error(-20882,'INVENTORY_TASK_READ_CELL_ARTICLE_FORBIDDEN');end if;
  elsif RRL_ACCESS_API.allowed(p_actor,'stock_inventory_count','WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(ware))!=1 then
   raise_application_error(-20882,'INVENTORY_CURRENT_READ_SCOPE_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20884,'INVENTORY_READ_SOURCE_NOT_FOUND');end;
 procedure claim_task(p_task number,p_actor varchar2)is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();n number;state varchar2(20);owned boolean:=false;locked_actor varchar2(50);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'INVENTORY_CLAIM_OUTSIDE_STOCK_REQUIRED');end if;
  task_authority(p_task,p_actor,'CLAIM');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INVENTORY_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RUSERS',p_actor);
  RRL_STOCK_LOCK_API.begin_plan;owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state is null or state not in('PREPARED','ACTIVE')then raise_application_error(-20860,'INVENTORY_CLAIM_RELEASE_CLOSED');end if;
  select INVENTORY_TASK_ID into n from RRL_INVENTORY_TASK where INVENTORY_TASK_ID=p_task for update;
  select ID into locked_actor from RUSERS where ID=p_actor for update;
  task_authority(p_task,p_actor,'CLAIM');
  update RRL_INVENTORY_TASK set STATUS='IN_PROGRESS',ASSIGNED_TO=p_actor,ASSIGNED_AT=nvl(ASSIGNED_AT,systimestamp),STARTED_AT=nvl(STARTED_AT,systimestamp),UPDATED_AT=systimestamp,UPDATED_BY=p_actor where INVENTORY_TASK_ID=p_task;
  RRL_STOCK_LOCK_API.clear_plan;
 exception when others then if owned then RRL_STOCK_LOCK_API.clear_plan;end if;raise;end;
end;
/
