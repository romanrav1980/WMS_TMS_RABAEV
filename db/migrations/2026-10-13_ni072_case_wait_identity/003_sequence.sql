-- Affected dev metadata only: avoid future self-task IDs colliding with the two earlier CASE-source IDs.
-- Sequence gaps are retained; rollback never rewinds a used task sequence.
declare max_source number;next_task number;iterations number:=0;begin
 select nvl(max(SOURCE_TASK_ID),0)into max_source from RRL_WAREHOUSE_TASK where TASK_SOURCE='MANUAL'and TASK_TYPE='PUTAWAY';
 loop
  select RRL_WAREHOUSE_TASK_SQ.nextval into next_task from dual;iterations:=iterations+1;
  exit when next_task>max_source;
  if iterations>=10000 then raise_application_error(-20886,'WAIT_TASK_SEQUENCE_CATCHUP_BOUND_REQUIRED');end if;
 end loop;
end;
/
