begin execute immediate 'alter table RRL_LOGISTICS_EXPENSE add COST_CORRECTION_OF_OP varchar2(100) references RRL_LOGISTICS_COST_RUN(OPERATION_ID)';
exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate 'create index RRL_LOG_EXP_COST_CORR_IDX on RRL_LOGISTICS_EXPENSE(COST_CORRECTION_OF_OP)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
