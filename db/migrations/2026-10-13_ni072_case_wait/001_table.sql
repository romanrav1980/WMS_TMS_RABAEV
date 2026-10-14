alter table RRL_ST_DEFER_WAIT_PLAN add CASE_TASK_ID number(12,0);
alter table RRL_ST_DEFER_WAIT_PLAN add constraint RRL_DWAIT_CASE_FK foreign key(CASE_TASK_ID)references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID);
alter table RRL_ST_DEFER_WAIT_PLAN add constraint RRL_DWAIT_CASE_CK check(CASE_TASK_ID is null or(BASE_QTY=1 and BASE_UOM='CASE'));
