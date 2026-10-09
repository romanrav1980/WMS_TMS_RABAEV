create or replace FUNCTION        RRL_SET_SCAN_PROOVE_SP_OLD(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2
) return int
 
accessible by(function RRL_SET_SCAN_PROOVE) IS
ttt number;
  SPIS_OTBOR_ON_SCAN_OPALL1 int;
  vhelp2 varchar2(255);
  
BEGIN


    if count_of_errors1=0 then
     update RABAEV.RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ; 
     
     DBMS_OUTPUT.put_line(  'flag1' );
     
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
     DBMS_OUTPUT.put_line(  'flag2' );

           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    '' );
                DBMS_OUTPUT.put_line(  'flag3' );

         end if;
     
          
     
    else
     update RABAEV.RRL_SBORKA_PALLETS set  prim=prim1 , COUNT_OF_ERRORS=count_of_errors1  where PALLET_UID=PALLET_UID1  ; 
    end if;
    

return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SCAN_PROOVE_SP_OLD;

/

create or replace FUNCTION        RRL_SET_SCAN_PROOVE2_SP_OLD(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2 , 
    SBORSHIK1  VARCHAR2,
    KLADOVSHIK1 VARCHAR2
) return int
 
accessible by(function RRL_SET_SCAN_PROOVE2) IS
vhelp2 varchar2(255);
ttt number;
 SPIS_OTBOR_ON_SCAN_OPALL1 int;
BEGIN


    if count_of_errors1=0 then
    
     update RABAEV.RRL_SBORKA_PALLETS set    PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ;
     
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    KLADOVSHIK1 );
         end if;
     
          
    else
     update RABAEV.RRL_SBORKA_PALLETS set   prim=prim1 , COUNT_OF_ERRORS=count_of_errors1  where PALLET_UID=PALLET_UID1  ; 
    end if;
    
    if (not(SBORSHIK1 is null)) then
     update RABAEV.RRL_SBORKA_PALLETS set  SBORSHIK=SBORSHIK1   where PALLET_UID=PALLET_UID1  ; 
    end if;
    
    if (not(KLADOVSHIK1 is null)) then
     update RABAEV.RRL_SBORKA_PALLETS set  KLADOVSHIK=KLADOVSHIK1   where PALLET_UID=PALLET_UID1  ; 
    end if;

return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SCAN_PROOVE2_SP_OLD;

/

create or replace FUNCTION        RRL_TRIAL_BY_WEIGHT_SP_OLD( 
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int accessible by(function RRL_TRIAL_BY_WEIGHT) IS 
    tmpVar number;
    pogr number;
    IDD1 int;
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);






update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT(PALLET_UID1)  )<pogr ) then
       
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = unistr('\041f\0440\043e\0432\0435\0440\0435\043d\0412\0435\0441\0430\043c\0438') where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = unistr('\0412\044b\0434\0430\043d \0432 \0441\0431\043e\0440\043a\0443') where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       
       RAISE;       
END RRL_TRIAL_BY_WEIGHT_SP_OLD;

/

create or replace FUNCTION        RRL_TRIAL_BY_WEIGHT2_SP_OLD( 
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int accessible by(function RRL_TRIAL_BY_WEIGHT2) IS 
    tmpVar number;
    pogr number;
    IDD1 int;
    SPIS_OTBOR_ON_SCAN_OPALL1 int;
    vhelp2 varchar2(255);
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);






update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT2(PALLET_UID1)  )<pogr ) then
       
        
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    user_id1 );
         end if;
        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = unistr('\041f\0440\043e\0432\0435\0440\0435\043d\0412\0435\0441\0430\043c\0438') where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = unistr('\0412\044b\0434\0430\043d \0432 \0441\0431\043e\0440\043a\0443') where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       
       RAISE;       
END RRL_TRIAL_BY_WEIGHT2_SP_OLD;

/

create or replace FUNCTION        RRL_UPDATE_PALLET_ROW2_SP_OLD( 
    articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2
 )
 
 RETURN varchar2 
 accessible by(function RRL_UPDATE_PALLET_ROW2) IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;
count_nesobrano int;
rhelp int;

BEGIN
    count_nesobrano:=0;
 select  TAREWEIGHT , ORDER_WEIGHT , TARESIZE , quantity , ORIGINAL_ORDER_WEIGHT , original_quantity
 into   TAREWEIGHT1 , ORDER_WEIGHT1 , TARESIZE1 , quantity1 , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
 from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 if(quantity1=0) then
 
     if( ORIGINAL_ORDER_WEIGHT1 >0 ) then
     
      koef := count1 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1 , VYCHERK_USER_ID = user_id1 
        ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4) 
        where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
         
        
     end if;
  

 else
    
    koef := count1 / quantity1 ;
       update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1 ,  VYCHERK_USER_ID = user_id1 
    ,ORDER_WEIGHT= round( ORDER_WEIGHT*koef , 4) 
    where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 end if;
 

 
begin
 
 select count(ID) into count_nesobrano from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ((QUANTITY<> sobrano) or (sobrano is null));
    if(count_nesobrano=0)then
        
        update RABAEV.RRL_SBORKA_PALLETs set PROOVED_BY_SCAN=1 , KLADOVSHIK=user_id1  where PALLET_UID = pallet_uid1  ;
        
        
        rhelp:=RABAEV.RRL_SET_SCAN_PROOVE2(
            PALLET_UID1    ,
            0 ,
            '' , 
            '',
            user_id1
        );
        
        RETURN 'PROOVED_BY_SCAN';
    end if;
exception WHEN NO_DATA_FOUND THEN null;
end;   
   
    RETURN 'ok';

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       
       RAISE;
END RRL_UPDATE_PALLET_ROW2_SP_OLD;

/

create or replace FUNCTION        RRL_UPDATE_PALLET_ROW3_SP_OLD(
    row_id1 int ,
    articul1 varchar2 ,
    pallet_uid1 varchar2 , 
    PACK_COUNT2 number , 
    QUANTITY2 number , 
    CURRENT_MOD_ID2 int , 
    ORDER_WEIGHT2 number , 
    PRIHOD_PALLET_UID2 varchar2 ,
    user_id1 varchar2
 )
 
 RETURN varchar2 
 accessible by(function RRL_UPDATE_PALLET_ROW3) IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;
count_nesobrano int;
rhelp int;
type_w1 int;
COUNT_SHT_IN_KOR1 int;
PACK_COUNT3 int; 
KARTON_WEIGHT3 number;
QUANTITY3 number;
 SHT_IN_KOR3 int;
SHT_WEIGHT3 number;
ORDER_WEIGHT3 number;
BEGIN

count_nesobrano:=0;
select art.type_w , COUNT_SHT_IN_KOR  into type_w1 , COUNT_SHT_IN_KOR1  from rrl_articuls art where art.ACTICUL= articul1; 



if( type_w1=0 ) then  
    if(COUNT_SHT_IN_KOR1= 0) or ( COUNT_SHT_IN_KOR1 is null ) then
                     return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0432\043b\043e\0436\0435\043d\043d\043e\0441\0442\044c. \0423\043a\0430\0436\0438\0442\0435 \0432\043b\043e\0436\0435\043d\043d\043e\0441\0442\044c.') );
    end if;

     select     ORDER_WEIGHT    , ORIGINAL_ORDER_WEIGHT , original_quantity
     into      ORDER_WEIGHT1   , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
     from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

          koef := QUANTITY2 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
          PACK_COUNT=round(QUANTITY/COUNT_SHT_IN_KOR1 , 2 ) , 
          QUANTITY = QUANTITY2 , 
          VYCHERK_USER_ID = user_id1 
          ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4)  ,
          PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 
          where id = row_id1 ; 

end if;  

if( type_w1=1 ) then    

     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                       return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0444\0430\0441\043e\0432\043a\0430. \0423\043a\0430\0436\0438\0442\0435 \0444\0430\0441\043e\0432\043a\0443.') );
     end if;

     select     ORDER_WEIGHT    , ORIGINAL_ORDER_WEIGHT , original_quantity
     into      ORDER_WEIGHT1   , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
     from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

     select SHT_IN_KOR into COUNT_SHT_IN_KOR1  from rrl_articul_mods where id=CURRENT_MOD_ID2 ; 

     koef := QUANTITY2 / original_quantity1 ;
     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=round(QUANTITY/COUNT_SHT_IN_KOR1 , 2 ) , 
     QUANTITY = QUANTITY2 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4)  ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

end if;  


if( type_w1=2 ) then    

     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                        return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0444\0430\0441\043e\0432\043a\0430. \0423\043a\0430\0436\0438\0442\0435 \0444\0430\0441\043e\0432\043a\0443.') );
        end if;

     if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                        return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \043f\0430\0440\0442\0438\044f. \0423\043a\0430\0436\0438\0442\0435 \043f\0430\0440\0442\0438\044e.') );
     end if;

    select round(  ORDER_WEIGHT2 / ( MOD_ID.KARTON_WEIGHT + MOD_ID.SHT_WEIGHT* MOD_ID.SHT_IN_KOR ) ,2 ) , MOD_ID.KARTON_WEIGHT
     into  PACK_COUNT3 , KARTON_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    select (ORDER_WEIGHT2 - PACK_COUNT3* KARTON_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT3 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

end if;  

if( type_w1=3 ) then    

     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                          return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0444\0430\0441\043e\0432\043a\0430. \0423\043a\0430\0436\0438\0442\0435 \0444\0430\0441\043e\0432\043a\0443.') );
        end if;

    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                          return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \043f\0430\0440\0442\0438\044f. \0423\043a\0430\0436\0438\0442\0435 \043f\0430\0440\0442\0438\044e.') );
    end if;

    select   MOD_ID.KARTON_WEIGHT
     into    KARTON_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    select (ORDER_WEIGHT2 - PACK_COUNT2* KARTON_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

end if;  



if( type_w1=6 ) then    

     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                        return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0444\0430\0441\043e\0432\043a\0430. \0423\043a\0430\0436\0438\0442\0435 \0444\0430\0441\043e\0432\043a\0443.') );
        end if;

    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                            return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \043f\0430\0440\0442\0438\044f. \0423\043a\0430\0436\0438\0442\0435 \043f\0430\0440\0442\0438\044e.') );
    end if;

    select   MOD_ID.KARTON_WEIGHT , MOD_ID.SHT_WEIGHT 
     into    KARTON_WEIGHT3 , SHT_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    if(SHT_WEIGHT3   = 0) or ( SHT_WEIGHT3 is null ) then
            return unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ')+articul1+unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d \0432\0435\0441 \0448\0442\0443\043a\0438 \0432 \0444\0430\0441\043e\0432\043a\0435.');
        end if;

    select (((ORDER_WEIGHT2 - PACK_COUNT2* KARTON_WEIGHT3 ) / SHT_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  ) )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

end if;  







if( type_w1=7 ) then    

     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
            return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0444\0430\0441\043e\0432\043a\0430. \0423\043a\0430\0436\0438\0442\0435 \0444\0430\0441\043e\0432\043a\0443.') );
        end if;

     if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
              return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \043f\0430\0440\0442\0438\044f. \0423\043a\0430\0436\0438\0442\0435 \043f\0430\0440\0442\0438\044e.') );
     end if;

    select   MOD_ID.KARTON_WEIGHT , MOD_ID.SHT_WEIGHT , MOD_ID.SHT_IN_KOR   
     into    KARTON_WEIGHT3 , SHT_WEIGHT3 , SHT_IN_KOR3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

     if(SHT_WEIGHT3   = 0) or ( SHT_WEIGHT3 is null ) then
            return    concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  ,unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d \0432\0435\0441 \0448\0442\0443\043a\0438 \0432 \0444\0430\0441\043e\0432\043a\0435.') );

     end if;

    if(SHT_IN_KOR3   = 0) or ( SHT_IN_KOR3 is null ) then
             return    concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  ,unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \0432\043b\043e\0436\0435\043d\043d\043e\0441\0442\044c \0448\0442\0443\043a\0438 \0432 \0444\0430\0441\043e\0432\043a\0435.') );
    end if;      

    begin 
        select (  PACK_COUNT2 * SHT_IN_KOR3     )   ,    PACK_COUNT2 * ( ( WEIGHT_BRUTTO - WEIGHT_TN ) / PRIHOD_PALLET.COUNT_KOR   )
        into QUANTITY3 ,   ORDER_WEIGHT3 from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;
    exception
        when no_data_found then return concat( concat( unistr('\041f\0440\0438\0445\043e\0434 \043f\043e \043f\0430\043b\043b\0435\0442\0443 ') , PRIHOD_PALLET_UID2 ) , unistr(' \043d\0435 \043e\0431\043d\0430\0440\0443\0436\0435\043d') );
        when others then return  concat( concat( unistr('\041f\0440\0438\0445\043e\0434 \043f\043e \043f\0430\043b\043b\0435\0442\0443 ') , PRIHOD_PALLET_UID2 ) , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d \0432\0435\0441, \0422\041d \043b\0438\0431\043e \043a\043e\043b\0438\0447. \043a\043e\0440\043e\0431\043e\043a. ')  );

    end;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT3 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

end if;  








if( type_w1=5 ) then    

begin 
    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                          return  concat( concat(unistr('\0414\043b\044f \0430\0440\0442\0438\043a\0443\043b\0430 ') , articul1)  , unistr(' \043d\0435 \0443\043a\0430\0437\0430\043d\0430 \043f\0430\0440\0442\0438\044f. \0423\043a\0430\0436\0438\0442\0435 \043f\0430\0440\0442\0438\044e.') );
    end if;

    select PRIHOD_PALLET.UNIT_COUNT * (ORDER_WEIGHT2 / ( PRIHOD_PALLET.WEIGHT_BRUTTO - PRIHOD_PALLET.WEIGHT_TN )  ) 
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; 

    exception 
    when no_data_found then return unistr('\041d\0435 \043d\0430\0439\0434\0435\043d\0430 \043f\0430\0440\0442\0438\044f');
    when others then return unistr('\043e\0448\0438\0431\043a\0430 RRL_UPDATE_PALLET_ROW3_SP_OLD');
    end;

end if;  



begin
 select count(ID) into count_nesobrano from RABAEV.RRL_SBORKA_PALLET_ROWS 
 where PALLET_UID = pallet_uid1  and ((QUANTITY<> sobrano) or (sobrano is null));
    if(count_nesobrano=0)then        
        update RABAEV.RRL_SBORKA_PALLETs set PROOVED_BY_SCAN=1 , KLADOVSHIK=user_id1  where PALLET_UID = pallet_uid1  ;
        rhelp:=RABAEV.RRL_SET_SCAN_PROOVE2(
            PALLET_UID1    ,
            0 ,
            '' , 
            '',
            user_id1
        );
        RETURN 'PROOVED_BY_SCAN';
    end if;
exception WHEN NO_DATA_FOUND THEN null;
end;   


RETURN 'ok';

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN unistr('\043d\0435 \043d\0430\0439\0434\0435\043d\043e');
      WHEN OTHERS THEN RAISE;
END RRL_UPDATE_PALLET_ROW3_SP_OLD;

/
