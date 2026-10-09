create or replace PROCEDURE        RRL_OTKAT_ORDER2 (
 order_id int 
 )
as

tmp_current_cond int;
tmp_v varchar2(50);
cursor dddd is

   SELECT   UID_PALLET  from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id ;
   
BEGIN
    
   tmp_current_cond:=0;

   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 )  then
        return;
   end if;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=0  where ID = order_id  ;
   
   if  ( tmp_current_cond=1 or tmp_current_cond=0 )  then
     delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   end if;


 for  articul_row in dddd loop
            tmp_v := articul_row.UID_PALLET ;
             delete from RABAEV.RRL_REMAINS where UID_POLETA= tmp_v ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA=tmp_v  ;
  end loop;



commit;

end;
/
