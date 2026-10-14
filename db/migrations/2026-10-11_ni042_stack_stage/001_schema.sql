alter table RRL_SKU_RECEIPT_POLICY add(STACK_STAGE varchar2(10)default 'MAIN'not null);
alter table RRL_SKU_RECEIPT_POLICY add constraint RRL_SKU_STACK_STAGE_CK check(STACK_STAGE in('BASE','MAIN','TOP'));
alter table RRL_CASE_PICK_LINE add(STACK_STAGE varchar2(10)default 'MAIN'not null,STACK_POLICY_VERSION number default 0 not null);
alter table RRL_CASE_PICK_LINE add constraint RRL_CASE_STACK_STAGE_CK check(STACK_STAGE in('BASE','MAIN','TOP')and STACK_POLICY_VERSION>=0);
