create or replace package RRL_STOCK_REPL_CONTINUATION authid definer
 accessible by(package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure plan_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_residual number,p_rows in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure create_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_domain json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_REPL_CONTINUATION as
 procedure plan_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_qty number,p_residual number,p_rows in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
  rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;v_fact number;v_next number;v_short number;v json_object_t:=json_object_t();
 begin
  if p_task.TASK_SOURCE!='WAVE' or p_task.TASK_TYPE!='REPLENISHMENT' or p_residual is not null then return;end if;
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
  select count(*) into v_short from RRL_CASE_PICK_SHORT where REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and RECOVERY_STATE='WAIT_REPLENISHMENT';
  if rt.MINIMAX_CYCLE_ID is not null or v_short>0 or rt.PICK_TASK_ID is not null then return;end if;
  select nvl(sum(m.BASE_QTY),0)+p_qty into v_fact from RRL_WAREHOUSE_TASK t join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
   where t.TASK_SOURCE='WAVE' and t.TASK_TYPE='REPLENISHMENT' and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
  if nvl(rt.DEMAND_BASE_QTY,rt.QTY)<=v_fact then return;end if;
  select RRL_PICK_WAVE_REPL_SQ.nextval into v_next from dual;
  RRL_STOCK_PLAN_HELPER.row_key(p_rows,'RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_next));
  RRL_STOCK_PLAN_HELPER.anchor(p_rows,70,'UNIQUE','REPL.CONT:'||RRL_STOCK_PLAN_HELPER.decimal_text(rt.PICK_WAVE_REPLENISH_TASK_ID));
  v.put('id',v_next);v.put('demand',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(rt.DEMAND_BASE_QTY,rt.QTY)));
  v.put('fact',RRL_STOCK_PLAN_HELPER.decimal_text(v_fact));v.put('remaining',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(rt.DEMAND_BASE_QTY,rt.QTY)-v_fact));
  p_domain.put('replenishment_continuation',v);
 end;
 procedure create_next(p_task RRL_WAREHOUSE_TASK%rowtype,p_domain json_object_t,p_actor varchar2) is
  rt RRL_PICK_WAVE_REPLENISH_TASK%rowtype;v json_object_t;v_fact number;v_id number;
 begin
  if not p_domain.has('replenishment_continuation') then return;end if;
  v:=p_domain.get_object('replenishment_continuation');v_id:=v.get_number('id');
  select * into rt from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task.SOURCE_TASK_ID;
  select nvl(sum(m.BASE_QTY),0) into v_fact from RRL_WAREHOUSE_TASK t join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
   where t.TASK_SOURCE='WAVE' and t.TASK_TYPE='REPLENISHMENT' and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID;
  if rt.STATUS!='DONE' or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(rt.DEMAND_BASE_QTY,rt.QTY))!=v.get_string('demand')
   or RRL_STOCK_PLAN_HELPER.decimal_text(v_fact)!=v.get_string('fact') then raise_application_error(-20890,'CLOSURE_CHANGED: replenishment remaining demand');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PICK_WAVE_REPLENISH_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_id)));
  rt.PARENT_REPLENISH_TASK_ID:=rt.PICK_WAVE_REPLENISH_TASK_ID;rt.PICK_WAVE_REPLENISH_TASK_ID:=v_id;
  rt.QTY:=RRL_STOCK_MATH.quantity(v.get_string('remaining'));rt.DEMAND_BASE_QTY:=rt.QTY;rt.STATUS:='RELEASED';
  rt.SOURCE_RESERVATION_ID:=null;rt.PALLET_UID:=null;rt.SOURCE_CELL_CODE:=null;rt.SOURCE_AVAILABLE_QTY:=null;
  rt.SOURCE_PRODUCED_DATE:=null;rt.SOURCE_EXPIRY_DATE:=null;rt.RELEASED_AT:=sysdate;rt.RELEASED_BY:=p_actor;
  rt.CREATED_AT:=sysdate;rt.CREATED_BY:=p_actor;rt.UPDATED_AT:=sysdate;rt.UPDATED_BY:=p_actor;
  rt.RESERVE_OPERATION_ID:='REPL.CONT.SOURCE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id);
  rt.WAIT_REASON:='Remaining demand after confirmed source pallet delivery';
  insert into RRL_PICK_WAVE_REPLENISH_TASK values rt;
 end;
end;
/
