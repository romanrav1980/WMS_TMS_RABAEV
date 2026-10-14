create or replace FUNCTION        RRL_UPDATE_SBORKA_PALLET_ROWS2(

PALLET_UID_to varchar2 ,
row_id_from int 


)
 RETURN INT 
 IS
 
PALLET_UID_from varchar2(255);
tmpVar int;
articul_temp varchar(255);
row_id_upd int;
count1 number;
count2 number;
tt varchar(200);

BEGIN
   tmpVar := 0;
 
select PR.ARTICUL  ,  PR.QUANTITY   , PR.PALLET_UID  into articul_temp , count2 , PALLET_UID_from from RRL_SBORKA_PALLET_ROWS PR where PR.ID = row_id_from ;

    if( PALLET_UID_from= PALLET_UID_to ) then 
        return row_id_from;
    end if;
    

    begin
        --   СМОТРИМ В ПРЕДЫДУЩЕМ ПАЛЛЕТЕ . 
        select PR.ID , PR.QUANTITY into row_id_upd , count1  from RRL_SBORKA_PALLET_ROWS PR where PR.PALLET_UID = PALLET_UID_to and PR.ARTICUL = articul_temp  ;
        --update RRL_SBORKA_PALLET_ROWS PR  set   PR. , selected=1 where ID = row_id_from ;    
--       tt:= RRL_UPDATE_PALLET_ROW2( row_id_upd  ,    count1+count2 , 'MOVE' ); 
        tt:= RRL_UPDATE_PALLET_ROW2( articul_temp   ,  PALLET_UID_to  ,    count1+count2 , 'MOVE' ); 
        
        if( PALLET_UID_from <> PALLET_UID_to ) then 
            
            delete  from RRL_SBORKA_PALLET_ROWS   where  ID = row_id_from;
            
        end if;
        
    exception
        when no_data_found then
        -- Если в паллете, куда переностися строка нет таких артикулов.   
            update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = PALLET_UID_to , selected=1 where ID = row_id_from ;
        when others then RAISE;
          
    end;

   
   RETURN tmpVar;
    
END RRL_UPDATE_SBORKA_PALLET_ROWS2;
/
