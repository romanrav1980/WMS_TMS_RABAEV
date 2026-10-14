begin execute immediate 'alter table RRL_LOGISTICS_EXPENSE add(ADJUSTMENT_SIGN number(1) default 1 not null check(ADJUSTMENT_SIGN in(-1,1)),CORRECTION_OF_OP varchar2(100) references RRL_LOGISTICS_EXPENSE(OPERATION_ID),EXPECTED_CONFIRMED_TOTAL number(27,2))';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate 'create index RRL_LOG_EXP_CORRECTION_IDX on RRL_LOGISTICS_EXPENSE(CORRECTION_OF_OP)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
