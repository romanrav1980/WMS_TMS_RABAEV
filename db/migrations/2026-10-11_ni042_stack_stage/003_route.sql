create or replace package RRL_CASE_ROUTE_ADMISSION authid definer accessible by(package RRL_STOCK_CASE_PICK_CMD) as
 procedure assert_next(p_case number,p_line number);
end;
/

create or replace package body RRL_CASE_ROUTE_ADMISSION as
 procedure assert_next(p_case number,p_line number) is
  v_stage number;v_next_stage number;v_group_max number:=0;v_rank number;v_rows number;v_known number;v_pending_unknown number;v_next number;v_passed number;
 begin
  select PICK_SEQUENCE,case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end into v_rank,v_stage from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and CASE_PICK_LINE_ID=p_line;
  select count(*),count(PICK_SEQUENCE),
   sum(case when PICK_SEQUENCE is null and nvl(STATUS,'NEW')not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY then 1 else 0 end),
   min(case when nvl(STATUS,'NEW')not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY then PICK_SEQUENCE end),
   max(case when nvl(PICKED_QTY,0)>0 then PICK_SEQUENCE end)
  into v_rows,v_known,v_pending_unknown,v_next,v_passed
  from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case;
  if v_rows>200 then raise_application_error(-20881,'CASE_ROUTE_LINE_BOUND_200');end if;
  -- Issued stages must fit the original one-way route; never reverse it by sorting weights.
  for point in(select PICK_SEQUENCE,
    min(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end) LO,
    max(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end) HI
   from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and PICK_SEQUENCE is not null
    and nvl(STATUS,'NEW')!='CANCELLED'and(case when STATUS='SHORT_PICKED'then nvl(PICKED_QTY,0)else PLANNED_QTY end)>0
   group by PICK_SEQUENCE order by PICK_SEQUENCE)loop
   if point.LO<v_group_max then raise_application_error(-20886,'CASE_STACK_ROUTE_CONFLICT');end if;
   v_group_max:=point.HI;
  end loop;
  select min(case STACK_STAGE when 'BASE'then 1 when 'TOP'then 3 else 2 end)into v_next_stage
   from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_case and nvl(STATUS,'NEW')not in('DONE','CANCELLED','SHORT_PICKED')and nvl(PICKED_QTY,0)<PLANNED_QTY
    and(PICK_SEQUENCE=v_rank or(v_known=0 and PICK_SEQUENCE is null));
  if v_next_stage is not null and v_stage!=v_next_stage then raise_application_error(-20886,'CASE_STACK_EARLIER_STAGE_UNFINISHED');end if;
  -- Legacy DIRECT cases without any assigned route keep the original contract.
  if v_known=0 then return;end if;
  if v_rank is null or v_pending_unknown>0 then raise_application_error(-20886,'CASE_ROUTE_ASSIGNED_SEQUENCE_REQUIRED');end if;
  if v_passed is not null and v_rank<v_passed then raise_application_error(-20886,'CASE_ROUTE_BACKTRACK_FORBIDDEN');end if;
  if v_next is not null and v_rank!=v_next then raise_application_error(-20886,'CASE_ROUTE_EARLIER_POINT_UNFINISHED');end if;
 end;
end;
/
