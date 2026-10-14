declare n number;
begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_PLAN_TARGET_I';
 if n=0 then execute immediate 'create index RRL_IW_PLAN_TARGET_I on RRL_INTERWARE_PLAN(TARGET_TT_ID,OPERATION_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_DEC_TARGET_I';
 if n=0 then execute immediate 'create index RRL_IW_DEC_TARGET_I on RRL_INTERWARE_DECISION(TARGET_TT_ID,PLAN_OPERATION_ID,REVISION_NO)';end if;
end;
/
