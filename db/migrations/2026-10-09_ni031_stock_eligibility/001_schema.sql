-- MIGRATION_ID 2026-10-09-007-stock-source-eligibility
-- Existing warehouse SKU rule owns explicit direct receipt picking.
declare n number;
begin
 select count(*) into n from user_tab_columns where TABLE_NAME='RRL_RECEIPT_SKU_RULE' and COLUMN_NAME='SOURCE_PICK_MODE';
 if n=0 then execute immediate q'[alter table RRL_RECEIPT_SKU_RULE add SOURCE_PICK_MODE varchar2(20) default 'AFTER_PUTAWAY' not null]';end if;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_RECEIPT_SOURCE_MODE_CK';
 if n=0 then execute immediate q'[alter table RRL_RECEIPT_SKU_RULE add constraint RRL_RECEIPT_SOURCE_MODE_CK check(SOURCE_PICK_MODE in('AFTER_PUTAWAY','DIRECT'))]';end if;
end;
/
