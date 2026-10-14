declare v_expression varchar2(32767);n number;
begin
 select COLUMN_EXPRESSION into v_expression from USER_IND_EXPRESSIONS where INDEX_NAME='RRL_TT_HU_LOAD_UID_U1'and COLUMN_POSITION=1;
 if instr(upper(v_expression),'CUSTODY_RELEASED_AT')>0 then return;end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_TT_HU_LOAD_UID_V2_U1';
 if n=0 then execute immediate q'[create unique index RRL_TT_HU_LOAD_UID_V2_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED')and CUSTODY_RELEASED_AT is null then ROOT_UID end)]';end if;
 -- New uniqueness is installed before the original index is replaced.
 execute immediate 'drop index RRL_TT_HU_LOAD_UID_U1';
 execute immediate 'alter index RRL_TT_HU_LOAD_UID_V2_U1 rename to RRL_TT_HU_LOAD_UID_U1';
end;
/
