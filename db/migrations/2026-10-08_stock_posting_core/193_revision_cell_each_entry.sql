create or replace function RRL_REVIZION_CELL(
 CELL1 varchar2,count1 number,user_id1 varchar2,
 p_operation_id varchar2 default null,p_revision_id number default null,
 p_uid varchar2 default null,p_reason varchar2 default null) return varchar2 authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_REVIZION_CELL_SP_OLD(CELL1,count1,user_id1);end if;
 return RRL_STOCK_INV_ENTRY.count_lot(CELL1,p_uid,RRL_STOCK_PLAN_HELPER.decimal_text(count1),
  'EA',p_revision_id,user_id1,p_operation_id,p_reason);
end;
/
