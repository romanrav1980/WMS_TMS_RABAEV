begin execute immediate 'alter table RRL_LOGISTICS_EXP_ALLOC_LINE add(WEIGHT_SOURCE varchar2(30) not null,WEIGHT_BOX_UID varchar2(200))';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
