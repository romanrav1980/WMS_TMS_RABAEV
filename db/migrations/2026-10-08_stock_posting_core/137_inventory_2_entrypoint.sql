create or replace function RRL_INV_CREATE_LINE2(cell1 varchar2,shk_art varchar2,articul_part varchar2,count1 number,p_revision_id number default null,p_expiry date default null,p_actor varchar2 default null,p_operation_id varchar2 default null) return varchar2 authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_INV_CREATE_LINE2_SP_OLD(cell1,shk_art,articul_part,count1);end if;
 return RRL_STOCK_INV_ENTRY.register_line(cell1,shk_art,articul_part,count1,p_revision_id,p_expiry,p_actor,p_operation_id);
end;
/
