alter table RRL_RECEIPT_WARE_SETTINGS add(DEFER_WAIT_CELL varchar2(50));
/
create or replace trigger RRL_DEFER_WAIT_CELL_GUARD
before insert or update of DEFER_WAIT_CELL,WARE_ID on RRL_RECEIPT_WARE_SETTINGS
for each row
declare n number;
begin
 if :new.DEFER_WAIT_CELL is not null then
  select count(*)into n from RRL_CELLS c where c.CELL=:new.DEFER_WAIT_CELL and c.WARE_ID=:new.WARE_ID
   and nvl(c.OTBOR,0)=0 and nvl(c.IS_SYSTEM,0)=0 and c.EXPEDITION_GROUP is null
   and nvl(c.BLOCKED_FOR_ACCEPT,0)=0 and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0
   and not exists(select 1 from RRL_TOPOLOGY_CELL tc where tc.WARE_ID=c.WARE_ID and tc.LEGACY_CELL_CODE=c.CELL
    and tc.ACTIVE=1 and tc.CELL_KIND in('TRANSPORT_STAGING','GATE','FILM_WRAP')
    and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=c.WARE_ID and STATUS='PUBLISHED'));
  if n!=1 then raise_application_error(-20886,'DEFER_WAIT_CELL_SAME_WARE_OPEN_STORAGE_OUTSIDE_SHIPPING_REQUIRED');end if;
 end if;
end;
/
