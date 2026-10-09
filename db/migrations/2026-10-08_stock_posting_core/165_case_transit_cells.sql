-- Dedicated unavailable-for-allocation transit location; CASE commands alone enter/leave it.
declare v varchar2(20);n number;cell_id varchar2(60);ware number;system_flag number;blocked number;begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'TRANSIT_SETUP_REQUIRES_PREPARED');end if;
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');
 for w in(select ID from RRL_WARES where ID>0 order by ID) loop
  cell_id:='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(w.ID);
  select count(*) into n from RRL_CELLS where CELL=cell_id;
  if n=0 then
   insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,IS_SYSTEM,OTBOR,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)
    values(cell_id,w.ID,0,0,0,1,0,1,1);
  else
   select WARE_ID,IS_SYSTEM,BLOCKED_FOR_REMAINS into ware,system_flag,blocked from RRL_CELLS where CELL=cell_id;
   if ware!=w.ID or system_flag!=1 or blocked!=1 then raise_application_error(-20887,'CASE_TRANSIT_CONFIGURATION_CONFLICT');end if;
  end if;
 end loop;
 RRL_STOCK_CONFIG_API.end_change;
 commit;
exception when others then
 rollback;RRL_STOCK_CONFIG_API.end_change;raise;
end;
/
