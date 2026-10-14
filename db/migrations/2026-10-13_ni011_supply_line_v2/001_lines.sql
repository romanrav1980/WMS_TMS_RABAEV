declare
 n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20801,'RABAEV/orcl only');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_SUPPLY_ORDER'and COLUMN_NAME='GATEWAY_CONTRACT_VERSION';
 if n=0 then execute immediate 'alter table RRL_SAP_SUPPLY_ORDER add(GATEWAY_CONTRACT_VERSION number default 1 not null constraint RRL_SAP_SUP_CONTRACT_CK check(GATEWAY_CONTRACT_VERSION in(1,2)))';end if;
 for x in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_SAP_SUPPLY_LINE'and CONSTRAINT_NAME in('RRL_SAP_SUP_ROW_UK','RRL_SAP_SUP_ART_UK'))loop
  execute immediate 'alter table RRL_SAP_SUPPLY_LINE drop constraint '||x.CONSTRAINT_NAME;
 end loop;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_SAP_SUP_ROW_IX';
 if n=0 then execute immediate 'create index RRL_SAP_SUP_ROW_IX on RRL_SAP_SUPPLY_LINE(ROW_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_SAP_SUP_ART_IX';
 if n=0 then execute immediate 'create index RRL_SAP_SUP_ART_IX on RRL_SAP_SUPPLY_LINE(ORDER_ID,ARTICUL)';end if;
end;
/
