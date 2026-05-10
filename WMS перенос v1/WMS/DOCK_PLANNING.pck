create or replace package DOCK_PLANNING is

   function IS_AUTO_PLAN_DOCK(  TT_ID int) return int ;
     
   
end DOCK_PLANNING;
/
create or replace package body DOCK_PLANNING is

 
  function IS_AUTO_PLAN_DOCK(  TT_ID int) return int is
      AUTO_PLAN_DOCK1 int;   
  begin
    
    select max( WR.AUTO_PLAN_DOCK ) AUTO_PLAN_DOCK into AUTO_PLAN_DOCK1 from RRL_SBORKA_PALLETS PAL , RRL_WARES WR
    where PAL.Transtask_Id=TT_ID and WR.ID=ware_id ;
           return AUTO_PLAN_DOCK1;
           
  exception when no_data_found then return 0;
     when others then return 0; 
  end;

begin
 null;
end DOCK_PLANNING;
/
