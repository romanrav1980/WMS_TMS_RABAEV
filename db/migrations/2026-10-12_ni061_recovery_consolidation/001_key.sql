declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_IW_RECOVERY_DISPATCH'and CONSTRAINT_NAME='RRL_IW_REC_DISPATCH_PK';
 if n=0 then execute immediate 'alter table RRL_IW_RECOVERY_DISPATCH drop constraint SYS_C0018245';execute immediate 'alter table RRL_IW_RECOVERY_DISPATCH add constraint RRL_IW_REC_DISPATCH_PK primary key(OPERATION_ID,ST_ID)';end if;
end;
/
