create or replace FUNCTION        ftime_shipping_plan( 
STDATE date ,
SHIPPING_TIME varchar2 
 )
 RETURN date
 --По дате создания накладной и плановому времени отгрузки возвращает плановое время-дата отгрузки
 IS 
 ret date;
 STDATE1 date;
 h_hours int;


BEGIN



    STDATE1:=STDATE;
    h_hours:=0;
    ret := STDATE;
    -- ЕСЛИ КОЛИЧЕСТВО ЧАСОВ > 12 , то  День отгрузки  = STDATE + 2 
    -- ЕСЛИ КОЛИЧЕСТВО ЧАСОВ <= 12 , то  День отгрузки  = STDATE + 1 
    
    if(   to_number( substr( SHIPPING_TIME  , 0 ,2 ) ) > 20 ) then 
        STDATE1:=  STDATE ;

    else
        STDATE1:=STDATE+1;

    end if;
    
    ret := to_date( concat ( to_char( STDATE1 ) , concat( ' ' , SHIPPING_TIME ) ) , 'dd.mm.yy HH24:MI'   ) ;
    
    
    
    
    
    return ret;

exception when others then return STDATE;



END ftime_shipping_plan;

/
