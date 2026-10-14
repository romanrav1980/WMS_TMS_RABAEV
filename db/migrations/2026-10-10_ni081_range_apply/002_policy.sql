create or replace package RRL_PICK_RANGE_POLICY authid definer as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number;
end;
/
create or replace package body RRL_PICK_RANGE_POLICY as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number is
  n number;identity number;v_mode varchar2(20);operation varchar2(100);
 begin
  select count(*),max(s.PICK_FACE_ARTICUL_ID),max(s.MODE_CODE),max(s.APPROVAL_OPERATION_ID)
   into n,identity,v_mode,operation from RRL_PICK_RANGE_STATUS s
   join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ARTICUL_ID=s.PICK_FACE_ARTICUL_ID
   join RRL_PICK_FACE f on f.PICK_FACE_ID=a.PICK_FACE_ID
   where f.CELL_CODE=p_cell and a.ARTICUL=p_article and s.MODE_CODE in('DRAINING','CLOSED');
  if n=0 then return 1;end if;
  if n!=1 or v_mode!='DRAINING'or p_repl is null or p_quantity is null then return 0;end if;
  select count(*)into n from RRL_PICK_RANGE_ALLOW_REPL where PICK_FACE_ARTICUL_ID=identity
   and DRAIN_OPERATION_ID=operation and REPLENISH_TASK_ID=p_repl and MAX_ORIGINAL_QTY>=p_quantity;
  return case when n=1 then 1 else 0 end;
 end;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number is
  q number;c varchar2(100);a varchar2(40);
 begin
  if p_exclude_repl is not null then
   begin
    select QTY,TARGET_CELL_CODE,ARTICUL into q,c,a from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_exclude_repl;
    if c!=p_cell or a!=p_article then return 0;end if;
   exception when no_data_found then return 0;end;
  end if;
  return target_write_allowed(p_cell,p_article,p_exclude_repl,q);
 end;
end;
/
