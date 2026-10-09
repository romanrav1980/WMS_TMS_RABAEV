create or replace function RRL_REVIZION_CELL_KOR(
 CELL1 varchar2,count_kor2 varchar2,user_id1 varchar2,p_revision_id number default null,
 p_operation_id varchar2 default null,p_uid varchar2 default null,p_reason varchar2 default 'Measured pick-face inventory')
 return varchar2 authid definer is state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_REVIZION_CELL_KOR_SP_OLD(CELL1,count_kor2,user_id1);end if;
 return RRL_STOCK_INV_ENTRY.count_lot(CELL1,p_uid,count_kor2,'BOX',p_revision_id,user_id1,p_operation_id,p_reason);
end;
/
