declare n number;begin
select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TARE_LOSS_CLAIM' and COLUMN_NAME='SOURCE_CLAIM_ID';
if n=0 then execute immediate 'alter table RRL_TARE_LOSS_CLAIM add(SOURCE_CLAIM_ID varchar2(100) references RRL_STOCK_OPERATION(OPERATION_ID),TRANSPORT_TASK_ID number references RRL_TRANSPORT_TASK(ID))';end if;
end;
/
begin execute immediate 'create index RRL_TARE_LOSS_SOURCE_IX on RRL_TARE_LOSS_CLAIM(SOURCE_CLAIM_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
