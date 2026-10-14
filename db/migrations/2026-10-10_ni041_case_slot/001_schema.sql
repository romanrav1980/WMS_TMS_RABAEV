declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SLOT_CLAIM' and COLUMN_NAME='HU_CASE_TASK_ID';
 if n=0 then
  execute immediate 'alter table RRL_RECEIPT_SLOT_CLAIM add HU_CASE_TASK_ID number(10)';
  execute immediate 'alter table RRL_RECEIPT_SLOT_CLAIM add constraint RRL_HU_CLAIM_CASE_FK foreign key(HU_CASE_TASK_ID) references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID)';
  execute immediate 'create unique index RRL_HU_CLAIM_CASE_U1 on RRL_RECEIPT_SLOT_CLAIM(HU_CASE_TASK_ID)';
 end if;
end;
/
