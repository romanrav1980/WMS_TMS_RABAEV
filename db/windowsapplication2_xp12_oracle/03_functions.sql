DROP FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int

) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD ;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD2 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int

) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD ;
/


DROP FUNCTION RABAEV.RRL_GET_PALLET_CHECK_TIMES;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_PALLET_CHECK_TIMES( puid varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor dddd is
select to_char(time1 , 'dd.mm.yyyy HH24:MI:SS' ) time2, weight , user_id from RRL_SBORKA_PALLETS_HISTORY where ( PALLET_UID = puid ) and event='WEIGHT_CHECK' ;


BEGIN
   tmpVar := '';
   
   for f in dddd loop
        
    tmpVar:=concat(concat(Concat(concat(tmpVar  , concat( f.time2 , concat( ' = ' ,  f.weight ))) , 'u='  ) , f.user_id ) , ' ;');
   
   end loop;
   

   --select Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) )  into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   if(tmpVar is null) then
   tmpVar:='НЕ ПРОВЕРЯЛСЯ';
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ПРОВЕРЯЛСЯ';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return tmpVar;
       RAISE;
END RRL_GET_PALLET_CHECK_TIMES;
/


DROP FUNCTION RABAEV.RRL_IS_PALLET_LIKE_FAKE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_is_PALLET_like_fake( puid varchar2 )
 RETURN int IS 
tmpVar int;

BEGIN
   tmpVar := 0;
   select count( distinct WEIGHT ) into tmpVar from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' group by PALLET_UID  ;
if(  tmpVar>2) then
 tmpVar:=1;
   else
 tmpVar:=0;
end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 1;
       RAISE;
END RRL_is_PALLET_like_fake;
/


DROP FUNCTION RABAEV.RRL_ST_UNIQPCOUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ST_UNIQPCOUNT( ST varchar2 )
 RETURN int IS 
tmpVar number;
itogo int;
sobrano int;
 -- ВОЗВРАЩАЕТ КОЛИЧЕСТВО ПАЛЛЕТ, СОДЕРЖАЩИХ САХАР
BEGIN

   itogo := 0;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
--select  count(DISTINCT R.PALLET_UID)  into itogo from   RRL_SBORKA_PALLET_ROWS R , RRL_ARTICULS  A 
--   where   (  R.PALLET_UID = ST ) and ( R.ARTICUL=A.ACTICUL ) and ( A.PALLET_MULTIPLE<>1 ) ;

select  count(DISTINCT R.PALLET_UID)  into itogo from   RRL_SBORKA_PALLET_ROWS R  
   where   (  R.PALLET_UID = ST ) and  ( R.ARTICUL in ( 'Т0000008795' , 'Т0000127793' , 'Т0000127794'   ) );


   RETURN itogo+1;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
        RETURN -2;
END RRL_ST_UNIQPCOUNT;
/


DROP FUNCTION RABAEV.RRL_SUGAR_HAS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SUGAR_HAS( ART varchar2 )
return int
is
BEGIN

    if( ART= 'Т0000008795' ) then 
        return 1;
    end if;


    if( ART= 'Т0000127793' ) then 
        return 1;
    end if;

    if( ART= 'Т0000127794' ) then 
        return 1;
    end if;

return 0;


END RRL_SUGAR_HAS;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PALLETS_ADD2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLETS_ADD2 (
    ST_NUMBER1   varchar2,
    ADDR1 varchar2,
    PALLET_NUMBER1 INTEGER ,
    PALLET_UID1     VARCHAR2 ,
    STATE1    VARCHAR2 ,
    STDATE1 Date ,
    NAPR1 varchar2 ,
    USER_ID1 varchar2 ,
    ware_id1 int
) return int
IS

    ID1 int;
    DONE1 int;
    COND1 varchar2(255) ;

BEGIN


select ID into ID1 from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_UID1 ;
begin

    select R.STATE into COND1 from RABAEV.RRL_SBORKA_PALLETS R  where PALLET_UID = PALLET_UID1 ;
    select IN_PROCESS  into DONE1 from RABAEV.RRL_SBORKA_PALLETS_COND where COND=COND1;
    
    if ( DONE1=1)  then 
        return ID1;
    end if;
    
    delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID1;
    
    exception
    when NO_DATA_FOUND then
    NULL;
end;

delete from  RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_UID1 ;

update RRL_SBORKA_PALLETS set  STATE = STATE1 , NAPR = NAPR1 where  PALLET_UID = PALLET_UID1 ;


return ID1;
exception
    when NO_DATA_FOUND then
    begin
        INSERT INTO RABAEV.RRL_SBORKA_PALLETS (
              ADDR ,  
              ST_NUMBER      ,
              WARE_ID        ,
              PALLET_NUMBER  ,
              PALLET_UID     ,
              STATE ,
              NAPR ,
              STDATE , 
               USER_ID

      ) VALUES (
                ADDR1 ,
              ST_NUMBER1      ,
              WARE_ID1        ,
              PALLET_NUMBER1  ,
              PALLET_UID1     ,
              STATE1 ,
              NAPR1 ,
              STDATE1 ,
               USER_ID1
        
        );
        
        SELECT RRL_SBORKA_PALLETS_SQ.CURRVAL INTO ID1 FROM DUAL;
    return ID1;
    end;
    
END  RRL_SBORKA_PALLETS_ADD2 ;
/


DROP FUNCTION RABAEV.RRL_MAY_DELETE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_MAY_DELETE ( ST_N varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(6);
t2 int;

BEGIN

 return 'yes';
 
 select count( P.ID ) into t2 from RRL_SBORKA_PALLETS P where P.ST_NUMBER=ST_N and P.TRANSTASK_ID>0; 

 if(t2>0) then 
    return  'no';
 end if;
 
   tmpVar := 'no';

select IN_PROCESS into tmpVar from ( select CC.IN_PROCESS    
     from RABAEV.RRL_SBORKA_PALLETS PP , RABAEV.RRL_SBORKA_PALLETS_COND CC
     where  PP.ST_NUMBER=ST_N  and PP.STATE = CC.COND  and  CC.IN_PROCESS =1 ) where ROWNUM<=1 ; 


     if(tmpVar=1) then
        return 'no';
     else
        return 'yes';
     end if;
     
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'yes';
     WHEN OTHERS THEN
       RAISE;
END RRL_MAY_DELETE;
/


DROP FUNCTION RABAEV.ADD_RRL_TR_VEHICLE;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_TR_VEHICLE(
  ID1 int ,
  NUM1 varchar2 , 
  TR_TYPE1 varchar2 , 
  MARKA1  varchar2 ,
  REF_REJIM1 varchar2 ,
  WORKOINGNOW int ,
  PALLETS1 int , 
  LOPATA int

)
 RETURN INT 
 
 IS

    tmpVar int;
    nnn varchar2(50);

BEGIN
   tmpVar := 0;
   
   begin
   
    select ID into tmpVar from  RABAEV.RRL_TR_VEHICLE  where ID=  ID1 ;
    
    update  RABAEV.RRL_TR_VEHICLE set     NUM =  NUM1      ,
                  TR_TYPE =  TR_TYPE1  ,
                  MARKA  = MARKA1    ,
                  REF_REJIM = REF_REJIM1 , WORKING_NOW = WORKOINGNOW , PALLETS= PALLETS1 , GIDROBORT = LOPATA where  ID=  ID1 ;
    return tmpVar;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
       
            INSERT INTO RABAEV.RRL_TR_VEHICLE (

                  NUM        ,
                  TR_TYPE    ,
                  MARKA      ,
                  REF_REJIM  ,
                  WORKING_NOW  , 
                  PALLETS , 
                  GIDROBORT
                  
              ) VALUES (
                  NUM1        ,
                  TR_TYPE1    ,
                  MARKA1      ,
                  REF_REJIM1  ,
                  WORKOINGNOW ,
                  PALLETS1 , 
                  LOPATA
            );
            
            SELECT RABAEV.RRL_TR_VEHICLE_SQ.CURRVAL INTO tmpVar FROM DUAL;
           return tmpVar;
       end;

     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
   

    
commit;

   
   RETURN tmpVar;
   
   
 
       
END ADD_RRL_TR_VEHICLE;
/


DROP FUNCTION RABAEV.RRL_GIVE_TERMINAL_TASK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_TERMINAL_TASK( USER_ID1 varchar2 )
RETURN varchar2 
IS 
    tmp varchar2(255);
BEGIN
 tmp:='';
 -- НАХОДИМ ЗАДАЧУ ДЛЯ ДАННОГО ЮЗЕРА 

select PALLET_UID into tmp from ( 
    select PP.PALLET_UID   from RABAEV.RRL_SBORKA_PALLETS  PP
    where ( SBORSHIK =  USER_ID1 )
      and ( PROOVED_BY_SCAN=0 and PROOVED=0 ) order by PP.STDATE DESC , PP.ADDR , PP.ORD  

) where rownum=1 ;


   RETURN  tmp;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN '';
END RRL_GIVE_TERMINAL_TASK;
/


DROP FUNCTION RABAEV.RRL_DELETE_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_DELETE_CELL(
cell4 varchar2 
)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_REMAINS C where C.CELL=cell4;
        
        
        
        
        
    exception
    when NO_DATA_FOUND THEN
            delete from RABAEV.RRL_CELLS   where CELL=cell4 and IS_SYSTEM<>1 ;
                
            WHEN OTHERS THEN
                   null;
    end;


 RETURN 1;
   
  
END RRL_DELETE_CELL;
/


DROP FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD2;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD2 (

    NAKLAD_NUMBER varchar2,
    DATE_OF_NAKLAD date,
    DATE_OF_ACCEPT date,
    POSTAVSHIK_NAME varchar2,
    SM_NAKLAD_NUMBER varchar2 ,
    ZAKAZ_NUMBER1 varchar2,
    ware_id1 int
) return int
IS
ID int;

BEGIN
    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD (
      ID,
    NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER , 
    ZAKAZ_NUMBER ,
    ware_id
      
  ) VALUES (
          RABAEV.RRL_PRIH_ORD_ID.NEXTVAL,
           NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER ,
    ZAKAZ_NUMBER1 ,
    ware_id1
    
    );
    
    SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD2;
/


DROP FUNCTION RABAEV.UPDATE_RRL_MOD;

CREATE OR REPLACE FUNCTION RABAEV.UPDATE_RRL_MOD (

  ID1             INTEGER,
  ARTICUL1        VARCHAR2,
  NAME1           VARCHAR2,
  SHT_IN_KOR1     INTEGER,
  SHT_WEIGHT1     NUMBER,
  KARTON_WEIGHT1  NUMBER,
  DELETED1        INTEGER
  
) return int
IS
ID2 int;

BEGIN
  

if ID1>0 then

    update  RABAEV.RRL_ARTICUL_MODS
    set 
      ID             = ID1,
      ARTICUL        = ARTICUL1,
      NAME           = NAME1,
      SHT_IN_KOR     = SHT_IN_KOR1 ,
      SHT_WEIGHT     = SHT_WEIGHT1 ,
      KARTON_WEIGHT  = KARTON_WEIGHT1,
      DELETED        =DELETED1
    where ID=ID1;
return ID1;
else

      INSERT INTO RABAEV.RRL_ARTICUL_MODS(
          ID , 
          ARTICUL        ,
          NAME           ,
          SHT_IN_KOR     ,
          SHT_WEIGHT     ,
          KARTON_WEIGHT  ,
          DELETED        
      ) VALUES (
          RABAEV.MODS_SEQ.NEXTVAL,
          ARTICUL1      ,
          NAME1          ,
          SHT_IN_KOR1     ,
          SHT_WEIGHT1     ,
          KARTON_WEIGHT1  ,
          DELETED1                      
        );
        
    SELECT MODS_SEQ.CURRVAL INTO ID2 FROM DUAL;
    
end if;
    
    return ID2;
    
END  UPDATE_RRL_MOD;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PALLETS_ADD;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLETS_ADD (
    ST_NUMBER1   varchar2,
    ADDR1 varchar2,
    PALLET_NUMBER1 INTEGER ,
    PALLET_UID1     VARCHAR2 ,
    STATE1    VARCHAR2 ,
    STDATE1 Date ,
    NAPR1 varchar2 ,
    ware_id1 int
) return int
IS

    ID1 int;
    DONE1 int;
    COND1 varchar2(255) ;

BEGIN


select ID into ID1 from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_UID1 ;
begin

    select R.STATE into COND1 from RABAEV.RRL_SBORKA_PALLETS R  where PALLET_UID = PALLET_UID1 ;
    select IN_PROCESS  into DONE1 from RABAEV.RRL_SBORKA_PALLETS_COND where COND=COND1;
    
    if ( DONE1=1)  then 
        return ID1;
    end if;
    
    delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID1;
    
    exception
    when NO_DATA_FOUND then
    NULL;
end;

delete from  RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_UID1 ;

update RRL_SBORKA_PALLETS set  STATE = STATE1 , NAPR = NAPR1 where  PALLET_UID = PALLET_UID1 ;


return ID1;
exception
    when NO_DATA_FOUND then
    begin
        INSERT INTO RABAEV.RRL_SBORKA_PALLETS (
              ADDR ,  
              ST_NUMBER      ,
              WARE_ID        ,
              PALLET_NUMBER  ,
              PALLET_UID     ,
              STATE ,
              NAPR ,
              STDATE

      ) VALUES (
                ADDR1 ,
              ST_NUMBER1      ,
              WARE_ID1        ,
              PALLET_NUMBER1  ,
              PALLET_UID1     ,
              STATE1 ,
              NAPR1 ,
              STDATE1
        
        );
        
        SELECT RRL_SBORKA_PALLETS_SQ.CURRVAL INTO ID1 FROM DUAL;
    return ID1;
    end;
    
END  RRL_SBORKA_PALLETS_ADD ;
/


DROP FUNCTION RABAEV.RRL_TT_VERYFY_PERC;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_VERYFY_PERC( IDTT int )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where  TRANSTASK_ID  = IDTT and PROOVED=1;

    if(itogo=0) then
        return 0;
    end if;


tmpVar:= sobrano / itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VERYFY_PERC;
/


DROP FUNCTION RABAEV.RRL_ST_VERYFY_PERC;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ST_VERYFY_PERC( ST varchar2 )
 RETURN int IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
 --  return 0;
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  ST_NUMBER  = ST;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where   ST_NUMBER  = ST and ( PROOVED=1 or  PROOVED_BY_SCAN=1 );

    if(itogo=0) then
        return 0;
    end if;


tmpVar:= sobrano *100/ itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
        RETURN -2;
END RRL_ST_VERYFY_PERC;
/


DROP FUNCTION RABAEV.RRL_PAL_VOLUME;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PAL_VOLUME( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID   ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_VOLUME;
/


DROP FUNCTION RABAEV.RRL_PAL_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PAL_WEIGHT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum(  R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID   ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_TT_DROP;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_DROP( IDTT int )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN

tmpVar := 1;
  
update RABAEV.RRL_SBORKA_PALLETS set TRANSTASK_ID = null where  TRANSTASK_ID  = IDTT;
update RRL_TRANSPORT_TASK set  DELETED=1 where ID = IDTT;
commit;
RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_TT_DROP;
/


DROP FUNCTION RABAEV.CALC_TIMESTAMP_DIFF_IN_SECONDS;

CREATE OR REPLACE FUNCTION RABAEV.CALC_TIMESTAMP_DIFF_IN_SECONDS (ts1 in timestamp, ts2 in timestamp)
           return number is total_secs number;
           diff interval day(9) to second(6);
       begin
       
       diff := ts2 - ts1;
       
       total_secs := abs(extract(second from diff) + extract(minute from diff)*60 + 
        extract(hour from diff)*60*60 +
        extract(day from diff)*24*60*60
        );
        
       return total_secs;
    end CALC_TIMESTAMP_DIFF_IN_SECONDS;
/


DROP FUNCTION RABAEV.RRL_TT_VODITEL_COMPANY;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_VODITEL_COMPANY( VODITEL_ID1 int )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN

    tmpVar := '';
  
    select  DOVERENNOST_OT into tmpVar from RABAEV.RRL_TR_VODITEL VOD   where  VOD.ID = VODITEL_ID1 ;
 
    RETURN tmpVar;
   
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VODITEL_COMPANY;
/


DROP FUNCTION RABAEV.RRL_TT_ADDR_COUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ADDR_COUNT( TTID int )
 RETURN int IS 
    tmpVar int;
BEGIN

select count( distinct RRL_SBORKA_PALLETS.ADDR  ) into tmpVar
from RABAEV.RRL_SBORKA_PALLETS,  RABAEV.RRL_ADDR  
where TRANSTASK_ID=TTID   ;
   
if(tmpVar=0 ) then 
return 0;
end if;

   RETURN tmpVar-1;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 0;
       RAISE;
END RRL_TT_ADDR_COUNT;
/


DROP FUNCTION RABAEV.RRL_COPY_PALLET_ROW2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_COPY_PALLET_ROW2( 
    row_id2 int ,
    count1  number , 
    PALLET_UID_NEW    VARCHAR2 
 )
 
 RETURN int 
 IS 
 
 ID1 int;
  PALLET_UID1    VARCHAR2(255) ;
  ARTICUL1       VARCHAR2(255) ;
  SHORTNAME1     VARCHAR2(1255) ;
  SHTRIHKOD1     VARCHAR2(255) ;
  EI1            VARCHAR2(255) ;
  TAREWEIGHT1    NUMBER;
  PATH1          VARCHAR2(1255) ;
  ORDER_WEIGHT1  NUMBER;
  TARESIZE1      NUMBER;
 QUANTITY1       NUMBER;
  SORTFIELD1     INTEGER;
  AUCTION1       VARCHAR2(255);
  DOCID1         VARCHAR2(255) ;
  ORIGINAL_QUANTITY1 number;
   ORIGINAL_ORDER_WEIGHT1 number;
  ware_id1 int ;
  PACK_COUNT1 int;
 

BEGIN
  
if( count1<=0) then 
    return 0;
end if;

--------------------------------------------------------------------------------------------
 

      select  PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT  into 
              
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1 ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 , 
              ORIGINAL_QUANTITY1 ,
              ORIGINAL_ORDER_WEIGHT1     
              from RABAEV.RRL_SBORKA_PALLET_ROWS where ID= row_id2 ;



SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID_NEW    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              (count1* ORIGINAL_ORDER_WEIGHT1/ORIGINAL_QUANTITY1 )  ,
              TARESIZE1      ,
              count1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              ORIGINAL_QUANTITY1,
              ORIGINAL_ORDER_WEIGHT1
            );

 
   
--update   RABAEV.RRL_SBORKA_PALLET_ROWS set QUANTITY = QUANTITY - count1 where ID = row_id2  ; 
--------------------------------------------------------------------------------------------

   RETURN ID1;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_COPY_PALLET_ROW2;
/


DROP FUNCTION RABAEV.RRL_OP_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_OP_WEIGHT( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;


BEGIN
   tmpVar := 0;
select sum(  R.ORDER_WEIGHT )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    R.PALLET_UID = PALLET_UID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_OP_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_UPDATE_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_CELL(
cell4 varchar2 ,
X1 int ,
Y1 int ,
Z1 int , 
ware_id4 int

)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_CELLS C where C.CELL=cell4;
        
        
        update RABAEV.RRL_CELLS set X=X1 , Y=Y1 , Z=Z1 , ware_id= ware_id4   where CELL=cell4 ;
        
        
    exception
            WHEN NO_DATA_FOUND THEN
                insert into RABAEV.RRL_CELLS (
                      CELL  ,
                      OTBOR    ,
                      BLOCKED_FOR_REMAINS    ,
                      BLOCKED_FOR_POPOLNENIE ,
                      X                      ,
                      Y                      ,
                      Z                      ,
                      BLOCKED_FOR_ACCEPT     ,
                      WARE_ID          
                )  
                values 
                (   
                    cell4 ,
                    1 ,
                    0 ,
                    0 ,
                    X1 ,
                    Y1 ,
                    Z1 ,
                    0,
                    ware_id4
                );
            WHEN OTHERS THEN
                   null;
    end;


 RETURN 1;
   
  
END RRL_UPDATE_CELL;
/


DROP FUNCTION RABAEV.RRL_UPDATE_TT_ZONE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_TT_ZONE
(  
  ZONE1      VARCHAR2, 
  SUB_ZONE1  VARCHAR2, 
  DOCK1      VARCHAR2 ,  
  X1 number , 
  Y1 number 
)
 RETURN int IS
 tmp_var varchar2(255);

BEGIN

    select SUB_ZONE1 into  tmp_var  from RRL_TT_ZONES where SUB_ZONE  = SUB_ZONE1 ;
    update RRL_TT_ZONES set zone=zone1 , dock = dock1 , X=X1 , Y=Y1  where sub_zone = sub_zone1 ;

   RETURN 0;
exception
when no_data_found then 
    insert into RABAEV.RRL_TT_ZONES ( ZONE , SUB_ZONE , DOCK , X , Y   ) values ( ZONE1 , SUB_ZONE1 , DOCK1 , X1 , Y1 );
   RETURN 0;
END  RRL_UPDATE_TT_ZONE;
/


DROP FUNCTION RABAEV.RRL_GIVE_KARSH_STAT_INFO;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_KARSH_STAT_INFO( 
user_id1 varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := 'пусто';
   
   
   
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'пусто';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GIVE_KARSH_STAT_INFO;
/


DROP FUNCTION RABAEV.OBJ2NUMBER;

CREATE OR REPLACE FUNCTION RABAEV.obj2number( 
par1 number 
 )
 RETURN number 
 IS 
 

BEGIN
    
    if( par1 is null ) then
       RETURN 0;   
    end if;
    return par1;
    
exception
    when others then
    return 0;
END obj2number;
/


DROP FUNCTION RABAEV.RRL_TT_ZONE_EMPTY;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ZONE_EMPTY
(  
  time1      timestamp, 
  SUB_ZONE1  VARCHAR2
)
-- ПРОцедура дает количество паллет, находящихся в данной зоне в данный момент времени
RETURN number IS

count_of_pal int;
 
BEGIN

--return 0;

count_of_pal:=0;
select count( PAL.PALLET_UID ) into count_of_pal 
    from RABAEV.RRL_SBORKA_PALLETS PAL where   ZONE_TIME_PLAN_IN <= time1 and
    time1<= ZONE_TIME_PLAN_OUT and ZONE = SUB_ZONE1 ;


if( count_of_pal >0 ) then 
    return count_of_pal;
else
    return 0;
end if;


   RETURN 1;
exception

    when no_data_found then 
       RETURN 1;
    when others then return 1;

END  RRL_TT_ZONE_EMPTY;
/


DROP FUNCTION RABAEV.RRL_GET_TT_PRICE_ID;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_TT_PRICE_ID  
 ( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor ss is
select DISTINCT upper(ADDR1.REGION) REGION , upper(ADDR1.RAION) RAION  from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id
order by upper(ADDR1.REGION) , upper(ADDR1.RAION) ;

BEGIN
   tmpVar := '[]';
   
   select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tmpVar from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
   
   for s in ss  loop
   
    tmpVar:= Concat( Concat( concat( concat( tmpVar , upper( trim( s.REGION) ) )  , '-') , upper( trim(s.RAION) )) , ';' ) ;
   
   end loop;
 
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'no_transp_task';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_PRICE_ID;
/


DROP FUNCTION RABAEV.RRL_GET_TT_PRICE_ID2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_TT_PRICE_ID2  
 ( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

--  

cursor ss is
select DISTINCT upper(ADDR1.REGION) REGION    from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id
order by upper(ADDR1.REGION)   ;

BEGIN
   tmpVar := '[]';
   
   select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tmpVar from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
   
   for s in ss  loop
   
    tmpVar:= Concat(  concat( tmpVar ,   s.REGION    ) , ';' ) ;
   
   end loop;
 
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'no_transp_task';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_PRICE_ID2;
/


DROP FUNCTION RABAEV.RRL_ACCEPT_ORDER2_3;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ACCEPT_ORDER2_3 (
 order_id int ,
 user_id1 varchar2
 ) return int
is
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;
infin int;
cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN

infin:=0;   
   DBMS_OUTPUT.put_line( 'flag 1'); 
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return 0;
   end if;
   
   DBMS_OUTPUT.put_line( 'flag 2'); 
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
    if(infin>1000) then  return 0; end if;
 
    
 
 infin:=infin+1;
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 

    while tmpVar>0 loop
          begin
        
        if(infin>1000) then  return 0; end if;
        infin:=infin+1;
    
        if( articul_row_NORMA_UKLADKI<=0 ) then
            DBMS_OUTPUT.put_line( 'null' );
            return 0;
        end if;
        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
         
            
                DBMS_OUTPUT.put_line( tmp_uid_pallet);  
    
             delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             --delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID , kladovshik  ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              systimestamp  , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id , user_id1
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  


--commit;

return 0;

exception 
when no_data_found then null;
when others then  RAISE;

end  RRL_ACCEPT_ORDER2_3;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/


DROP FUNCTION RABAEV.ADD_RRL_OTHOD_NAKLAD;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_OTHOD_NAKLAD(
  NAKLADNAME1           VARCHAR2      ,
  MAG_NO1               VARCHAR2      ,
  NAKLADDATE1           DATE          ,
  CREATIONDATE1         DATE          ,
  PLANNEDDELIVERYDATE1  DATE ,
  ware_id1  int

)
 RETURN INT 
 
 IS

    tmpVar int;
    nnn varchar2(50);

BEGIN
   tmpVar := 0;
   
   begin
    select ID into tmpVar from  RABAEV.RRL_OTHOD_NAKLAD  where NAKLADNAME=  NAKLADNAME1 ;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
       
            SELECT RABAEV.RRL_PRIHOD_NAKLAD_SQ.NEXTVAL INTO tmpVar FROM DUAL;
   
            INSERT INTO RABAEV.RRL_OTHOD_NAKLAD (
              ID,
              NAKLADNAME   ,
              MAG_NO       ,
              NAKLADDATE   ,
              CREATIONDATE ,
              PLANNEDDELIVERYDATE ,
              ware_id
            ) VALUES (
                  tmpVar , 
                  NAKLADNAME1   ,
                  MAG_NO1       ,
                  NAKLADDATE1   ,
                  CREATIONDATE1 ,
                  PLANNEDDELIVERYDATE1 ,
                  ware_id1
            );
           return tmpVar;
       end;
     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
   

    
commit;

   
   RETURN tmpVar;
   
   
 
       
END ADD_RRL_OTHOD_NAKLAD;
/


DROP FUNCTION RABAEV.ADD_RRL_OTHOD_NAKLAD_ROWS;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_OTHOD_NAKLAD_ROWS(
ID_ROW1 int ,
    ID_NAKLAD1           int      ,
    ARTICUL1 varchar,
    COUNT2  number
)
 RETURN INT 
 IS
 
tmpVar int;
ID_ROW2 int;
cond1 int;

BEGIN
   tmpVar := 0;
   ID_ROW2:=0;
   
   select CONDITION into cond1  from RABAEV.RRL_OTHOD_NAKLAD where ID=ID_NAKLAD1 ;

    if(cond1>=2 ) then
        return 0;
    end if;  
       


    begin

        select  ID into ID_ROW2  from  RABAEV.RRL_OTHOD_NAKLAD_ROWS where ARTICUL=ARTICUL1  and ID_NAKLAD=ID_NAKLAD1 ;
    exception
        WHEN NO_DATA_FOUND THEN
            ID_ROW2:=0;
            
    end;




    if( ID_ROW2=0 ) then
    
      SELECT RABAEV.RRL_PRIHOD_NAKLAD_ROWS_SQ.NEXTVAL INTO tmpVar FROM DUAL;
      INSERT INTO RABAEV.RRL_OTHOD_NAKLAD_ROWS (
          ID,
          ID_NAKLAD   ,
          ARTICUL ,
          COUNT1      
      ) VALUES (
              tmpVar , 
              ID_NAKLAD1   ,
              ARTICUL1 ,
              COUNT2    
      );

    else

        update RABAEV.RRL_OTHOD_NAKLAD_ROWS set ARTICUL=ARTICUL1 , COUNT1=COUNT2 where ID= ID_ROW2;

    end if;

   RETURN tmpVar;
    
END ADD_RRL_OTHOD_NAKLAD_ROWS;
/


DROP FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD (

    NAKLAD_NUMBER varchar2,
    DATE_OF_NAKLAD date,
    DATE_OF_ACCEPT date,
    POSTAVSHIK_NAME varchar2,
    SM_NAKLAD_NUMBER varchar2 ,
    ware_id1 int
) return int
IS
ID int;

BEGIN
    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD (
      ID,
    NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER , 
    ware_id
      
  ) VALUES (
          RABAEV.RRL_PRIH_ORD_ID.NEXTVAL,
           NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER ,
    ware_id1
    
    );
    
    SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD;
/


DROP FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD_ROW;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD_ROW (
    NAKLAD_ID int,
    articul string,
    expiury_date date ,
    count1 NUMBER ,
    price Number
) return int
IS
ID int;

BEGIN

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
    ORDID ,
    ARTICUL ,
    EXPIRY_DATE,
    count1 ,
    price ,
    ID  
  ) VALUES (
    NAKLAD_ID ,
    articul , 
    expiury_date ,
    count1 ,
    price ,
    RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD_ROW;
/


DROP FUNCTION RABAEV.ADD_SFERA_EAN2;

CREATE OR REPLACE FUNCTION RABAEV.ADD_SFERA_EAN2 (

    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
) return int
IS
row_uid int;

BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    return row_uid;
END  ADD_SFERA_EAN2;
/


DROP FUNCTION RABAEV.RRL_ACCEPT_ORDER;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ACCEPT_ORDER ( order_id int )

RETURN NUMBER 
IS
tmpVar NUMBER;

cursor dddd is
   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
   
BEGIN
   tmpVar := 0;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   
 
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
   
   
   
              
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       NULL;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ACCEPT_ORDER;
/


DROP FUNCTION RABAEV.RRL_ADD_INV_LINE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ADD_INV_LINE
(

    CELL5         varchar2 , 
    articul5      varchar2 ,
    COUNT15        number ,
    date_of_expire5  date ,
    PRICE5  number ,
    inventory_id  int , 
    iser_id5 varchar2

)
 RETURN varchar2 IS
tmpVar varchar2(150);
tmp_uid_pallet varchar2(150);
new_event_id int ;

BEGIN

   tmpVar := '';
   -- СОЗДАЕМ НОВЫЙ ПАЛЛЕТ С АРТИКУЛОМ И СРОКОМ ГОДНОСТИ
   
  tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul5) ,'_G' ) , inventory_id ) , '_' ) , CELL5 )  ;
   
 /*
  begin 
  
    select UID_PALLET into tmpVar from RABAEV.RRL_PALLETS  where  UID_PALLET = tmp_uid_pallet ;


  exception
  
  WHEN NO_DATA_FOUND THEN
      */
        insert into RABAEV.RRL_PALLETS
          (
              UID_PALLET        ,
              ARTICUL           ,
              CREATION_DATE     ,
              EXPIRY_DATE       ,
              UNIT_COUNT        ,
              PRICE             ,
              PRIHOD_NAKLAD_ID  )  values 
          (
              tmp_uid_pallet , 
              articul5,
              SYSTIMESTAMP ,
              date_of_expire5 ,
              COUNT15 ,
              PRICE5 , 
              -1* inventory_id
          )  ;
  
  --end;




   -- ЗАПИСЫВАЕМ ЕГО КОЛИЧЕСТВо В ЯЧЕЙКУ
   
    SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( 
                      new_event_id ,
                      'INVENT',
                      cell5,
                      SYSTIMESTAMP , 
                      COUNT15 ,
                      1,
                      tmp_uid_pallet ,
                      iser_id5 ,
                      ( -1* inventory_id )
                      ) ;
    
   
   -- ***************************************************
   
   
   RETURN tmpVar;
  
       
END RRL_ADD_INV_LINE;
/


DROP FUNCTION RABAEV.RRL_CLOSE_OTHOD_NAKLAD;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLOSE_OTHOD_NAKLAD
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    naklad_num int ,
    iser_id21 varchar2 
)
 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);


cursor rowss is 
select * from RABAEV.RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD = naklad_num ;

--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS left join RABAEV.RRL_PALLETS on 
    RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET  
    where RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  order by RRL_PALLETS.EXPIRY_DATE  ; 


BEGIN

EXPEDITION_CELL:= concat( 'EX_' , naklad_num );
DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar from RABAEV.RRL_OTHOD_NAKLAD where ID = naklad_num;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;

/*
При закрытии отгрузочной накладной:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


for naklad_row in rowss loop

tmpVar:=0;
kolvo_otbora:=naklad_row.COUNT1;


    DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА НАКЛАДНОЙ!' );
   DBMS_OUTPUT.put_line(  naklad_row.ARTICUL );

    select CELL into  current_cell from  RABAEV.RRL_ARTICULS 
    where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;
    
    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );
    DBMS_OUTPUT.put_line(  current_cell );
    

    for  ddd8 in rests_in_cell loop
-- REMAIN
    
        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );
        DBMS_OUTPUT.put_line(   ddd8.REMAIN );
        DBMS_OUTPUT.put_line(   ddd8.EXPIRY_DATE );
        DBMS_OUTPUT.put_line(   ddd8.UID_POLETA );
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  
          
        
        if(kolvo_otbora>0) then
/*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
        
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла  
*/          
            if(kolvo_otbora <= ddd8.REMAIN )  then
                -- UID_POLETA
                
                
                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                    kolvo_otbora:=0;
                else
                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id,
                      current_cell, 
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      ddd8.REMAIN ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                      
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
                
            end if;      

   
        end if;
    end loop;


         DBMS_OUTPUT.put_line(  '  почти конец ' );   
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  

--если Количество_отбора > 0 
--    Делаем проводку из ячейки 'excess' на отгрузочную накладную
--Количество_отбора  = 0
--конец если
if(kolvo_otbora >0 )  then
                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      'EXCESS',
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                     concat( 'EXCESS_' , naklad_row.ARTICUL ) ,
                      iser_id21 ,
                      naklad_num
                      ) ;
kolvo_otbora:=0;
end if;

   DBMS_OUTPUT.put_line(  '  почти конец ' );   

end loop;

update  RABAEV.RRL_OTHOD_NAKLAD set condition = 2  where ID = naklad_num;
   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   


commit;

   RETURN 'ok';
END RRL_CLOSE_OTHOD_NAKLAD;
/


DROP FUNCTION RABAEV.RRL_GET_CELL_REMAIN;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_CELL_REMAIN( cell_id varchar2 )
 RETURN NUMBER IS 
tmpVar NUMBER;
BEGIN
   tmpVar := 0;
   select sum( REMAIN ) into tmpVar from RRL_REMAINS where CELL = cell_id group by CELL;
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_CELL_REMAIN;
/


DROP FUNCTION RABAEV.RRL_GIVE_NEXT_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_NEXT_CELL
(
    cell1 varchar2
)
 RETURN varchar2
  IS
tmpVar varchar2(50);
Y1 int ;
X1 int;
Z1 int ;
ware_id1 int ;

BEGIN

select  ware_id ,Y , X , Z into  ware_id1 , Y1 , X1 ,Z1 from RABAEV.RRL_CELLS where CELL = cell1 and BLOCKED_FOR_REMAINS=0 ;

select cell into tmpVar  from
 (select cell 
 from RABAEV.RRL_CELLS where  Z=Z1 and Y=Y1 and X>X1 and ware_id=ware_id1
  order by X )  where  ROWNUM <=1  ;



   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return 'no next';
     WHEN OTHERS THEN
           return 'err66';
       RAISE;
END RRL_GIVE_NEXT_CELL;
/


DROP FUNCTION RABAEV.RRL_GIVE_POPOLNENIE2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_POPOLNENIE2 
(
    PIKING_CELL varchar2 ,
    ware_id1 int   
)
RETURN varchar2 IS
articul1 varchar(50);
tmpVar  varchar(950);
id_pal  varchar(50);


cursor rrrr is     select CELL , UID_POLETA into tmpVar , id_pal from (
        select RRL_REMAINS.CELL , RRL_REMAINS.UID_POLETA 
        from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , 
        RABAEV.RRL_CELLS    
         where ARTICUL=articul1       
         and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
         and RRL_CELLS.CELL = RRL_REMAINS.CELL
         and RRL_REMAINS.REMAIN>0 and RRL_REMAINS.CELL<>PIKING_CELL
         and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1 
         
         and RRL_CELLS.OTBOR =0 
         
 --        and RRL_CELLS.WARE_ID = ware_id1
         order by EXPIRY_DATE ) 
     where  ROWNUM<=1  ;



BEGIN
-- по заданной ячейке отбора вычисляем артикул и 
-- выдаем паллет данного артикула с наименьшим сроком годноти, стоящий ближе всего
    begin  
      select  ACTICUL into articul1 from RABAEV.RRL_ARTICULS 
            where CELL=PIKING_CELL;
     EXCEPTION
         WHEN NO_DATA_FOUND THEN
         
           -- **************************************************************
         
         begin 
             
              select ARTICUL into articul1   from (
                select RRL_PALLETS.ARTICUL  
                from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS   
                 where   RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
                 and RRL_REMAINS.REMAIN>0  
                 and RRL_REMAINS.CELL = PIKING_CELL
                 
                ) 
                
             where  ROWNUM=1  ;
             EXCEPTION
         WHEN NO_DATA_FOUND THEN
           return 'not a picking cell';
         WHEN OTHERS THEN
           return 'error5';
         end;
         
         
           -- **************************************************************
         
          -- return 'no a picking cell';
         WHEN OTHERS THEN
           return 'error4';
    end;
    
/*
    select CELL , UID_POLETA into tmpVar , id_pal from (
        select RRL_REMAINS.CELL , RRL_REMAINS.UID_POLETA 
        from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , 
        RABAEV.RRL_CELLS    
         where ARTICUL=articul1       
         and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
         and RRL_CELLS.CELL = RRL_REMAINS.CELL
         and RRL_REMAINS.REMAIN>0 and RRL_REMAINS.CELL<>PIKING_CELL
         and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1 
         
         and RRL_CELLS.OTBOR =0 
         
         and RRL_CELLS.WARE_ID = ware_id1
         order by EXPIRY_DATE ) 
     where  ROWNUM=1  ;
     */
     
     for ddd in rrrr loop
        tmpVar :=    concat( concat( tmpVar , ddd.CELL ) , ' '   ) ;      
     end loop;

     
     

RETURN tmpVar;

   --RETURN concat(tmpVar , concat( ' = ','id_pal')  ) ;

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       return 'no pallet';
     WHEN OTHERS THEN
       return 'error7';  
END RRL_GIVE_POPOLNENIE2 ;
/


DROP FUNCTION RABAEV.RRL_INFO_PALLET_RESTS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INFO_PALLET_RESTS
(
    pallet_id varchar2 
)

 RETURN varchar2 IS
tmpVar varchar(250);

cursor rrrr is select cell , remain from rrl_remains where uid_poleta=pallet_id   and cell not like 'EX%' ;
                                                                                
                                                                                
BEGIN
tmpVar := '';
                    
for ddd in rrrr loop

tmpVar := concat( concat( concat( concat( tmpVar , ddd.Cell ) , '=' ) , to_char( ddd.remain )  ) , '; ' ) ;

--tmpVar :=    concat( tmpVar , pallet_id )    ;
                                                                    
end loop;


   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  'no rest';
     WHEN OTHERS THEN
       RETURN 'error';
END  RRL_INFO_PALLET_RESTS;
/


DROP FUNCTION RABAEV.RRL_INTERNAL_MOVE2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INTERNAL_MOVE2(
pallet_id varchar2 , 
cell_to varchar2 ,
count1 number ,
user_id1 varchar2
)

RETURN varchar2

IS
count2 number;
tmpVar NUMBER;
art1 varchar2(50) ;
is_otbor int;
remain_in_cell_to number;
checks_passed int;
cell_from1 varchar2(50);
cell_next varchar2(50);
debug_mode int;
new_event_uid int;

prihod_cond int;
cursor rrr is select * from RRL_REMAINS where CELL = cell_to;

BEGIN
    
prihod_cond:=0;
count2:=count1;
   debug_mode:=0;
   tmpVar := 0;
   is_otbor:=0;
   remain_in_cell_to:=0;
   checks_passed:=0;
   cell_from1:='NONE';




 -- ЕСЛИ списание на НЕДОСТАЧУ
if  ( pallet_id='NO_PALLET' ) then

    begin
        for fgr in rrr  loop
        --
             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );

        --
        end loop;
     exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL;
    
    end;

    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
    RETURN CONCAT('ok_' ,  cell_next );
end if;


-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?
begin
    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;

    if( (prihod_cond=1) or (prihod_cond=0) ) then
        return 'NAKLAD_NE_ZAKRYTA';
    end if;

   exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL; 
    
end;




    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА
    

    select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;
  -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;



        if(count2=0) then
            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
        end if;

    exception
        WHEN NO_DATA_FOUND THEN
        
        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   
        UID_POLETA=pallet_id and cell=cell_to;
         
            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
            RETURN CONCAT('ok_' ,  cell_next );
        

         WHEN OTHERS THEN
            begin
            
                    begin
                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА
                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where
                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;
                    exception
                
                        WHEN NO_DATA_FOUND THEN
                            return 'pallet byl otgruzen';
                        WHEN OTHERS THEN null;
                        --    return 'other pallet3';
                    end;

                         
                    if(count2=0) then
                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
                    end if;
                    


                    
            exception
            
                WHEN NO_DATA_FOUND THEN
                    return 'other pallet1';
                WHEN OTHERS THEN
                    return 'other pallet2';
            end;
         
            
    end;
    

if( cell_to=cell_from1 ) then 
    return 'cell_to=cell_from1';
end if;   
    

    if(count2=0) then
        return 'count2=0';
    end if;

begin
    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 
    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 
    select OTBOR into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;
exception
         WHEN NO_DATA_FOUND THEN
           return 'no_pallet_cell_to';
         WHEN OTHERS THEN
           return 'other pallet1';
end;


if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then

    begin
        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;
    exception
             WHEN NO_DATA_FOUND THEN
               remain_in_cell_to:=0;
             WHEN OTHERS THEN
               remain_in_cell_to:=0;
    end;

    if remain_in_cell_to is null then
    remain_in_cell_to:=0;
    end if;

    if(remain_in_cell_to<=0)  then
        checks_passed:=1;
    else
    return 'cell_not_empty';    
    end if;

else
    checks_passed:=1;
end if;

        
    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 
    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event
    -- type_event = 2 , UID_POLETA , USER_ID

    if( checks_passed=0 ) then
     return 'fault';
    end if;
    

  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
 TYPE_EVENT , UID_POLETA , USER_ID ) values
( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );

-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ

commit;

cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);


   RETURN CONCAT('ok_' ,  cell_next );
      
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       return 'err1';
     WHEN OTHERS THEN
       return 'err2';
END RRL_INTERNAL_MOVE2;
/


DROP FUNCTION RABAEV.RRL_SFERA_EAN_EAN_BL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_sfera_ean_EAN_BL
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_BL into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_BL;
/


DROP FUNCTION RABAEV.RRL_SFERA_EAN_EAN_KOR;

CREATE OR REPLACE FUNCTION RABAEV.RRL_sfera_ean_EAN_KOR
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_KOR into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_KOR;
/


DROP FUNCTION RABAEV.RRL_SFERA_EAN_EAN_SHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_sfera_ean_EAN_SHT
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_SHT into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_SHT;
/


DROP FUNCTION RABAEV.RRL_TIME_FOR_RESERV;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TIME_FOR_RESERV RETURN int IS

BEGIN
   RETURN 12;
END RRL_TIME_FOR_RESERV;
/


DROP FUNCTION RABAEV.RRL_UPDATE_ARTICUL_EX;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_ARTICUL_EX(
-- ПРОЦЕДУРА ДЛЯ АВТОМАТИЧЕСКОЙ ЗАКАЧКИ ДАННЫХ ИЗ EXCEL
--Артикул    
articul4 varchar2 ,
--Наименование артикула     
name4 varchar2, 
--секция    (На самом деле идентификатор склада)    
section4 varchar2 ,
--ряд           = Z 
Z int ,
--стеллаж       = X*3
X3 int , 
--ярус          = Y
Y int ,
--место         = +X
X int ,
-- мест в ряду    
count_in_layer int ,
-- рядов в паллете    
layer_in_pall int ,
-- штук в паллете    
count_in_pal int , 
-- Ячейка отбора   
cell4 varchar ,
--Вес коробки
weight_of_kor number ,

-- Штрих-код штуки  
unit_barkode varchar,
--  Штрих-код коробки
kor_barkode varchar

)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_CELLS C where C.CELL=cell4;
    exception
            WHEN NO_DATA_FOUND THEN
                insert into RABAEV.RRL_CELLS (
                        CELL  ,
                      OTBOR    ,
                      BLOCKED_FOR_REMAINS    ,
                      BLOCKED_FOR_POPOLNENIE ,
                      X                      ,
                      Y                      ,
                      Z                      ,
                      BLOCKED_FOR_ACCEPT     ,
                      WARE_ID          
                )  
                values 
                (   
                    cell4 ,
                    1 ,
                    0 ,
                    0 ,
                    X3*3+X ,
                    Y ,
                    Z ,
                    0,
                    1
                );
            WHEN OTHERS THEN
                   null;
    end;


--return '';


--DBMS_OUTPUT.put_line( ' Hello 1 ');

    begin

        select AAA.ACTICUL into tmpVar from RABAEV.RRL_ARTICULS AAA where AAA.ACTICUL =   articul4 ;

        update RABAEV.RRL_ARTICULS set 
             NORMA_UKLADKI = count_in_pal ,
             CELL  = cell4 ,
             NAME  = name4,
             UNIT_TYPE  =  'шт'    ,
           BARCODE_SHT= unit_barkode,
              BARCODE_KOR  = kor_barkode ,
              BARCODE_BL  =  '' ,
              WEIGHT_OF_KOR = weight_of_kor,
              COUNT_IN_ROW = count_in_layer,
              ROWS_IN_PAL = layer_in_pall 
        where  ACTICUL =   articul4 ;
       
    exception
        WHEN NO_DATA_FOUND THEN
           
            insert into RABAEV.RRL_ARTICULS  (
                  ACTICUL   ,
                  NORMA_UKLADKI ,
                  CELL   ,
                  NAME   ,
                  UNIT_TYPE     ,
                  BARCODE_SHT ,
                  BARCODE_KOR    ,
                  BARCODE_BL     ,
                  WEIGHT_OF_KOR  ,
                  COUNT_IN_ROW  ,
                  ROWS_IN_PAL   
            ) values (
                articul4 ,
                count_in_pal ,
                cell4 ,
                name4 ,
                'шт' , 
                unit_barkode ,
                kor_barkode ,
                '' ,
                weight_of_kor ,
                count_in_layer  ,
                layer_in_pall 
            );
        
         WHEN OTHERS THEN
           null;
    end;
   


   
   
   RETURN '';
   
  
END RRL_UPDATE_ARTICUL_EX;
/


DROP FUNCTION RABAEV.RRL_TT_ZONE_DISTANCE_TO_DOCK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ZONE_DISTANCE_TO_DOCK
-- МЕРА РАССТОЯНИЯ ОТ ДОКА (ЗОНЫ) до ЯЧЕЙКИ ОТГРУЗОЧНОЙ. 
-- Необходима для определения 
-- Мера близости ( место  , зона дока ) = ( расстояние по оси У ) + (растояние по оси Х)* (длину ряда)
-- Измеряется как расстояние До первой ячейки данной подзоны (ячейки с расстоянием = 1). если таковой нет, 	то не измеряем вообща
(  
  ZONE1      VARCHAR2, 
  SUB_ZONE1  VARCHAR2
)
 RETURN number IS
 ZONE_OF_CELL varchar2(255);
 X1 number;
 Y1 number;
 X_MAX number;
 Y_MAX number;
 X_MIN number;
 distance number;
 
BEGIN

distance:=0;
-- Если ячейка находится на той-же оси, что и ZONE1 , то расстояние = Y , иначе 
-- Расстояние =  100*( расстояние между ЗОНАМи по оси Х )  + ( расстояние от ячейки  до конца ряда ( т.е. последней ячейки в ряде.) )

select ZONE , X,Y  into ZONE_OF_CELL , X1 , Y1  from RRL_TT_ZONES where SUB_ZONE = SUB_ZONE1 ;
if ( ZONE_OF_CELL = ZONE1 ) then 
    return Y1;
else

    -- Находим параметры зоны, в которой находится ячейка - максимальная удаленность ячеек в зоне , и параметр X (максимальный)
    select max( X ) , max(Y)  into X_MAX , Y_MAX   from RRL_TT_ZONES where  ZONE = ZONE_OF_CELL ;
    -- Находим параметры зоны , с которой идет сравнение -  параметр  X 
    select min( X )  into X_MIN   from RRL_TT_ZONES where  ZONE = ZONE1 ;

-- Расстояние =  100*( расстояние между ЗОНАМи по оси Х )  + ( расстояние от ячейки  до конца ряда ( т.е. последней ячейки в ряде.) )
distance:= 1000*(  abs(X_MAX-X_MIN) ) + abs( Y_MAX-Y1 )  ;
return distance;
end if;


   RETURN 10000;
exception

    when no_data_found then 
       RETURN 100000;
    when others then return 1000000;

END  RRL_TT_ZONE_DISTANCE_TO_DOCK;
/


DROP FUNCTION RABAEV.RRL_TRASPORT_TASK_UPDATE2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TRASPORT_TASK_UPDATE2 (
    TT_ID    int ,
    TRANSTYPE1 varchar2 , 
    TRANSPORT1 varchar2 ,
    ROUTETYPE1 varchar2 ,
    WAVE1 Date ,
    SHIPMENT_DATE1 DATE , 
    VODITEL_ID1   INTEGER ,
    PRIMECHANIE1 varchar2 ,
    DOCK1 varchar2 , 
    user_id1 varchar2
    
) return int
IS
ID1 int;
BEGIN

   if( not WAVE1 is null ) then 

        update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 , SHIPMENT_TIME = WAVE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    else

        update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    end if;
    
    return  TT_ID ;

END  RRL_TRASPORT_TASK_UPDATE2 ;
/


DROP FUNCTION RABAEV.RRL_HAS_WRIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )
    RETURN int IS 
    tmpVar varchar2(255);
    
BEGIN

begin

--return 1;
select id into tmpVar from rusers where id=user_id and USER_GROUP='GLOBAL_ADMIN';
return 1;

exception
 WHEN NO_DATA_FOUND THEN
    null;
end;

    select  RUSERS.USER_GROUP into tmpVar from RUSERS , RABAEV.RIGHTS where 
            RUSERS.ID=user_id and RIGHTS.USER_GROUP=RUSERS.USER_GROUP and RIGHT1= wright_name ;

   
    RETURN 1;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_HAS_WRIGHT;
/


DROP FUNCTION RABAEV.RRL_INV_CREATE_LINE4;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INV_CREATE_LINE4
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int,
    expiury_date date 
)
    RETURN varchar2 IS 
    price Number;

    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;
--expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;

--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end
--==================================================================

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE4;
/


DROP FUNCTION RABAEV.RRL_INFO_CELL_RESTS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INFO_CELL_RESTS
(
    cell1 varchar2 
)

 RETURN varchar2 IS
tmpVar varchar(1250);

cursor rrrr is select   remain , uid_poleta , rrl_pallets.ARTICUL , rrl_pallets.EXPIRY_DATE  from rrl_remains , rrl_pallets   where rrl_remains.cell = cell1 
 and rrl_remains.UID_POLETA= rrl_pallets.UID_PALLET  
  ;
                                                                                
                                                                                
BEGIN
tmpVar := '';
                    
for ddd in rrrr loop

    tmpVar := concat( concat( concat( concat( tmpVar , concat( '[', ddd.ARTICUL )  ) , '-' ) , to_char( ddd.remain )  ) , ' ' ) ;
    tmpVar :=concat( '' , concat(  concat ( tmpVar  ,  to_char(  ddd.EXPIRY_DATE  , 'dd.mm.yyyy ' )    ) , '] ' ) ) ;

--tmpVar :=    concat( tmpVar , pallet_id )    ;
                                                                    
end loop;


   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  'no rest';
     WHEN OTHERS THEN
       RETURN 'слишком много значений';
END  RRL_INFO_CELL_RESTS;
/


DROP FUNCTION RABAEV.RRL_SYNC_ADDR;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SYNC_ADDR (
dummy int
)
RETURN INT
is
tmpVar INT;
 

cursor dddd is 
  ( SELECT DISTINCT rrl_sborka_pallets.addr, rrl_sborka_pallets.napr  FROM rrl_sborka_pallets left join RRL_ADDR on rrl_sborka_pallets.ADDR = RRL_ADDR.ADDR(+) where RRL_ADDR.ADDR is null );
   
  begin 
  
  tmpVar:=0;
    for addr_row in dddd loop
        tmpVar:=tmpVar+1;
        INSERT INTO RRL_ADDR (  addr, napr   ) VALUES (  addr_row.addr, addr_row.napr  ) ;
    end loop;


RETURN tmpVar ;
   END RRL_SYNC_ADDR;
/


DROP FUNCTION RABAEV.RRL_TT_SET_TRANSCOMMENT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_SET_TRANSCOMMENT (

  TRANS    VARCHAR2,
  TTID1    int

  
) return varchar2
IS
ID1 int;
LOPATA int;
count_fault_adr int;
htemp varchar2(255);

BEGIN


select TT.GIDROBORT into LOPATA  from RRL_TR_VEHICLE TT where TT.NUM = TRANS ;
if(LOPATA=1  ) then 
    return 'OK';
end if;



select count( DISTINCT AA.ADDR ) into count_fault_adr from RRL_SBORKA_PALLETS PP , RRL_ADDR AA where  ( PP.ID = TTID1 )  and ( PP.ADDR=AA.ADDR ) and  AA.STOL = 0 ;

if( count_fault_adr>0 ) then 
     htemp:= concat ( concat( 'У ' , concat( count_fault_adr , '  адреса(ов) нет подъемного стола, у машины #' ) ) ,  concat( TRANS ,  '# нет  гидроборта' ) );
     return  htemp;
end if;

return 'OK';

exception

when no_data_found then return 'Нет такого номера в базе';


END  RRL_TT_SET_TRANSCOMMENT;
/


DROP FUNCTION RABAEV.ISIF;

CREATE OR REPLACE FUNCTION RABAEV.isif( 
par1 int ,
par2 int 
 )
 RETURN int 
 IS 
 

BEGIN
    

if( par1 is null ) then
   RETURN 0;   
end if;
if( par2 is null ) then
   RETURN 0;   
end if;

if( par1 = par2 ) then
   RETURN 1;   
end if;

return 0;

END isif;
/


DROP FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD_ROW2;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_PRIH_NAKLAD_ROW2 (
    NAKLAD_ID int,
    articul1 varchar2,
    expiury_date date ,
    count1 NUMBER ,
    price Number , 
    kolpal1 Number , 
    srok_godnosti1 int
) return int
IS
ID int;

BEGIN


delete from  RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ORDID=NAKLAD_ID and ARTICUL=articul1  ;

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
    ORDID ,
    ARTICUL ,
    EXPIRY_DATE,
    count1 ,
    price ,
    ID  ,
    kolpal ,
    srok_godnosti
  ) VALUES (
    NAKLAD_ID ,
    articul1 , 
    expiury_date ,
    count1 ,
    price ,
    RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL ,
    kolpal1 ,
    srok_godnosti1
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO ID FROM DUAL;

    return ID;
END  ADD_RRL_PRIH_NAKLAD_ROW2;
/


DROP FUNCTION RABAEV.RRL_CLEAR_PRIH_NAKLAD_ROWS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLEAR_PRIH_NAKLAD_ROWS (
    NAKLAD_ID int
) return int
IS
ID2 int;

BEGIN

    select condition into ID2 from RABAEV.RRL_PRIHOD_NAKLAD where ID = NAKLAD_ID;
    
    if ID2=0 then
        delete from RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ORDID = NAKLAD_ID ;
        return 1;
    end if;
    
    return 0;
END  RRL_CLEAR_PRIH_NAKLAD_ROWS;
/


DROP FUNCTION RABAEV.RRL_COUNT_KOR;

CREATE OR REPLACE FUNCTION RABAEV.RRL_COUNT_KOR (
    ART varchar2  ,
    count1 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
BEGIN

ret:=0;
--select CARTON_WEIGHT into ttt from RRL_ARTICULS A where  A.ACTICUL=ART;
--ret2:=ttt*count1;
--return ret2;
select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;


return ttt;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
END  RRL_COUNT_KOR;
/


DROP FUNCTION RABAEV.RRL_CARTON_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CARTON_WEIGHT (
    ART varchar2  ,
    count1 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
kart number;
BEGIN

ret:=0;
select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
--ret2:=ttt*count1;
--return ret2;
select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;


return ttt*kart;

exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;

END  RRL_CARTON_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_TT_POGRESHNOST2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_POGRESHNOST2( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;
count_kor number;

BEGIN



-- RRL_COUNT_KOR2( ARTICUL , QUANTITY , CURRENT_MOD_ID )
 
 
  
--select min( ( rowss.ORDER_WEIGHT / RRL_COUNT_KOR(  rowss.ARTICUL  , rowss.QUANTITY ) ) ) into tmpVar   from rrl_sborka_pallet_rows rowss 
-- where (rowss.PALLET_UID = PALLET_UID1) and (rowss.ORDER_WEIGHT > 0)  and ( RRL_COUNT_KOR(  rowss.ARTICUL  , rowss.QUANTITY )>0 ); 



   tmpVar := 3.5;


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 3.5;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
       
END RRL_TT_POGRESHNOST2;
/


DROP FUNCTION RABAEV.RRL_AUTH2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_AUTH2
(
    login varchar2 , 
    pass1 varchar2 ,
    version1 varchar2 
    
)
 RETURN int
  IS
tmpVar int;

BEGIN

begin
select V.ALLOW into tmpVar  from RABAEV.RRL_VERSIONS V where V.VERSION = version1 and V.ALLOW=1;
EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -3;
     WHEN OTHERS THEN
           return -4;
       RAISE;
   
end;

select  ware_id into tmpVar  from RABAEV.RUSERS where ID = login and  PASS = pass1 and  DELETED=0 and PRAVO_ADMIN_LOGIN=1;
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_AUTH2;
/


DROP FUNCTION RABAEV.RRL_GET_ST_CHECK_TIMES;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_ST_CHECK_TIMES( st_id varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor dddd is
select to_char( max(time1) , 'dd.mm.yyyy HH24:MI:SS')   time2 ,  H.user_id  from RRL_SBORKA_PALLETS_HISTORY H , RRL_SBORKA_PALLETS P
        where ( H.PALLET_UID=P.PALLET_UID )   and  ( P.ST_NUMBER like concat( '%' , concat( st_id , '%' ) ) ) and event='WEIGHT_CHECK'
        group by   H.user_id
         ;


BEGIN
   tmpVar := '';
   
   for f in dddd loop
        
    tmpVar:=concat(concat(tmpVar  , concat( f.time2 , concat( ' = ' ,  f.user_id  ))) , ' ;');
   
   end loop;
   

   --select Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) )  into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   if(tmpVar is null) then
   tmpVar:='НЕ ПРОВЕРЯЛСЯ';
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ПРОВЕРЯЛСЯ';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return tmpVar;
       RAISE;
END RRL_GET_ST_CHECK_TIMES;
/


DROP FUNCTION RABAEV.RRL_ADD_TT_2_BILLINGORDER;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ADD_TT_2_BILLINGORDER( 
bill_id int ,
tt_id int ,
act int -- 0 Удалить 1  Добавить
)

RETURN varchar2 IS 

tmpVar varchar2(255);
temp_company1 varchar2(255);
is_closed int;
temp_comp2 varchar2(255);
sum_of number;

BEGIN
   tmpVar := 'OK';
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.

    select ORDE.CLOSED , ORDE.COMPANY into is_closed , temp_company1 from RABAEV.RRL_BILL_ORDERS ORDE where ORDE.ID = bill_id ;
    if ( is_closed>0 ) then
    return 'Счет на оплату закрыт.';
    end if;
   
   -- Проверяем, что компания счета совпадает с компанией рейса.
 
   begin
   select VOD.DOVERENNOST_OT , PRICE into temp_comp2 , sum_of from  RABAEV.RRL_TRANSPORT_TASK T , RRL_TR_VODITEL VOD where 
     VOD.ID = T.VODITEL_ID and T.ID = tt_id and VOD.DOVERENNOST_OT = temp_company1  ;
   exception when no_data_found then return 'Компания Рейса не равна компании счета';
    when others then null;
   end;
   
   -- Проверяем, что рейс рассчитан (сумма не нулевая)
   if(sum_of<=0) then
   return 'Сумма рейса не рассчитана';
   end if;
   
   if(act=1) then
       -- Иначе добавляем рейс ко счету.   
       update  RABAEV.RRL_TRANSPORT_TASK  TT set PAY_ORDER_ID = bill_id where TT.ID=tt_id;
   else
       
       update  RABAEV.RRL_TRANSPORT_TASK  TT set PAY_ORDER_ID = null where TT.ID=tt_id;
  
   end if;
   
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'Нет такого счета или рейса';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ADD_TT_2_BILLINGORDER;
/


DROP FUNCTION RABAEV.RRL_CLOSE_BILLINGORDER;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLOSE_BILLINGORDER( 
bill_id int ,
act int -- 0 ОТкрыть 1  Закрыть
)

RETURN varchar2 IS 

tmpVar varchar2(255);
temp_company1 varchar2(255);
is_payed int;
temp_comp2 varchar2(255);

BEGIN
   tmpVar := 'OK';
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
if(act=0) then
    select ORDE.PAYED   into  is_payed    from RABAEV.RRL_BILL_ORDERS ORDE where ORDE.ID = bill_id ;
    if ( is_payed>0 ) then
    return 'Счет на оплату уже был оплачен.';
    end if;
   
end if;

  update RABAEV.RRL_BILL_ORDERS set closed=act    where ID = bill_id ;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'Нет такого счета или рейса';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_CLOSE_BILLINGORDER;
/


DROP FUNCTION RABAEV.RRL_ST_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ST_WEIGHT( stnumber1 varchar2 )
 RETURN number IS 
tmpVar number;

BEGIN
   tmpVar := 0;
  
select sum( R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where p.ST_NUMBER=stnumber1 and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ST_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_PAY_BILLINGORDER;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PAY_BILLINGORDER( 
bill_id int ,
act int -- 0 ОТкрыть 1  Закрыть
)

RETURN varchar2 IS 



BEGIN
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
    if(act=1) then
       
      update RABAEV.RRL_BILL_ORDERS set payed=1    where ID = bill_id ;
       
    end if;


   RETURN 'OK';

END RRL_PAY_BILLINGORDER;
/


DROP FUNCTION RABAEV.RRL_BILLINGORDER_SUM;

CREATE OR REPLACE FUNCTION RABAEV.RRL_BILLINGORDER_sum( 
bill_id int 
)

RETURN varchar2 IS 

temp1 number;
BEGIN
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
   select sum( TT.PRICE ) into temp1 from RRL_TRANSPORT_TASK TT where TT.PAY_ORDER_ID = bill_id;

   RETURN temp1;
END RRL_BILLINGORDER_sum;
/


DROP FUNCTION RABAEV.DELETE_RRL_PRIH_NAKLAD_ROW;

CREATE OR REPLACE FUNCTION RABAEV.DELETE_RRL_PRIH_NAKLAD_ROW (
    ROW_ID1 int
) return varchar2
IS
order_id2 int;
cond1 int;

BEGIN

select r.ORDID into order_id2 from RABAEV.RRL_PRIHOD_NAKLAD_ROWS r where ID= ROW_ID1;

select r2.CONDITION into cond1 from RABAEV.RRL_PRIHOD_NAKLAD r2 where ID  = order_id2 ;

DBMS_OUTPUT.put_line(  'DELETE_RRL_PRIH_NAKLAD_ROW' );

    if cond1 = 0 then
        delete from RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ID= ROW_ID1;
        commit;
    else
        return concat( 'naklad is closed' , order_id2 );
    end if;


    return 'ok';
END  DELETE_RRL_PRIH_NAKLAD_ROW;
/


DROP FUNCTION RABAEV.RRL_TT_READY_PERC;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_READY_PERC( IDTT int )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLETS_COND C where  TRANSTASK_ID  = IDTT 
    and P.STATE = C.COND(+) and C.DONE=1;

tmpVar:= sobrano / itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_READY_PERC;
/


DROP FUNCTION RABAEV.RRL_CLEAR_OTHOD_NAKLAD2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLEAR_OTHOD_NAKLAD2(
    ID_NAKLAD1           int 
)
 RETURN INT 
 IS
 
tmpVar int;
cond1 int;

BEGIN
   tmpVar := 0;
   
   select CONDITION into cond1  from RABAEV.RRL_OTHOD_NAKLAD where ID=ID_NAKLAD1 ;

    if(cond1>=2 ) then
        return 0;
    end if;  

    begin
        delete from  RABAEV.RRL_OTHOD_NAKLAD_ROWS where  ID_NAKLAD=ID_NAKLAD1 ;  
    end;

commit;

   RETURN tmpVar;
    
END RRL_CLEAR_OTHOD_NAKLAD2;
/


DROP FUNCTION RABAEV.RRL_TT_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_WEIGHT( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum(  R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_TT_VOLUME;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_VOLUME( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VOLUME;
/


DROP FUNCTION RABAEV.RRL_TT_SUMM;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_SUMM( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
--select sum( R.TARESIZE )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
--     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_SUMM;
/


DROP FUNCTION RABAEV.RRL_CARTON_WEIGHT2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CARTON_WEIGHT2 
(
    ART varchar2  ,
    count1 int ,
    CURRENT_MOD_ID2 int
) return number
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
kart number;
BEGIN


-- если не указан номер МОДа, то действуем по обычной схеме

if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
    
    
    ret:=0;
    select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
    select  ( count1/ A.COUNT_SHT_IN_KOR   ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
    return round( ttt*kart , 2 );
    
else

    begin        

        select ( MS.KARTON_WEIGHT/ 1000 ) ,    ( count1/  MS.SHT_IN_KOR )    into kart , ttt
        from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
        
        return round( ttt*kart , 2) ;
        
    exception
       when NO_DATA_FOUND then 
        
        ret:=0;
        select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
        select  ( count1/ A.COUNT_SHT_IN_KOR  ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
        return round( ttt*kart , 2);
        when others then 
        return 0;
    
    end;
    
end if;


exception
when NO_DATA_FOUND then


    return 0;
    when others then 
    return 0;

END  RRL_CARTON_WEIGHT2;
/


DROP FUNCTION RABAEV.RRL_PALLET_WEIGHT2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PALLET_WEIGHT2(
    PALLET_UID1  varchar2 
 )
 
 RETURN number IS 
tmpVar number;
BEGIN

   tmpVar := 0;
   
select sum(  R.ORDER_WEIGHT + RRL_CARTON_WEIGHT2( ARTICUL , QUANTITY , CURRENT_MOD_ID )  )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    PALLET_UID =   PALLET_UID1  ; 




-- RRL_CARTON_WEIGHT( ARTICUL , QUANTITY ) 



   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PALLET_WEIGHT2;
/


DROP FUNCTION RABAEV.RRL_TT_BILL_RECALC_PRICE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_BILL_RECALC_PRICE
(
    login varchar2 
)
 RETURN int
  IS
  
  
tmpVar int;

cursor mainloop is
select
  PR.ID              ,  PR.PRICE_NAME      ,
  PR.PRICE           ,  PR.COMPANY         ,
  PR.RANGE1          ,  PR.PRICE_FOR_HOURS ,
  PR.TYPE_TR , 
  km.PRICE* PR.RANGE1 ppp
 from 
RABAEV.RRL_TRANSPORT_PRICE PR , RABAEV.RRL_TT_BILL_PRICE_KM KM  
where  PRICE_NAME like  concat( concat( '' , KM.TT ) , '%' )
and PR.RANGE1 >  KM.KM_FROM and  PR.RANGE1 <= KM.KM_TO and PR.PRICE_FOR_HOURS=0
and price_folder=0 and PR.PRICE_FOLDER=0 ;


BEGIN



    for ml in mainloop loop
            
            update RRL_TRANSPORT_PRICE set PRICE = ml.ppp where ID = ml.ID;
    
        
        
    end loop;

           return -1;




   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_TT_BILL_RECALC_PRICE;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD3;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD3 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int , 
  PACK_COUNT1 int


) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD3 ;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD4;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PALLET_ROWS_ADD4 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int , 
  PACK_COUNT1 int


) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    end;
    
    when others then 
    begin
    
     delete from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;
    
            SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD4 ;
/


DROP FUNCTION RABAEV.ADD_HISTORY_NOTE;

CREATE OR REPLACE FUNCTION RABAEV.ADD_HISTORY_NOTE (

  USER_ID1    VARCHAR2,
  ADDR_TO1    VARCHAR2,
  ADDR_FROM1  VARCHAR2,
  MESS1       VARCHAR2,
  PUID1       VARCHAR2,
  COUNT12     NUMBER
  
) return int
IS
ID1 int;

BEGIN
select RRL_HISTORY_NOTE_SQ.NEXTVAL into ID1 from dual;

    INSERT INTO RABAEV.RRL_HISTORY_NOTES (
  ID         ,
  USER_ID   ,
  ADDR_TO   ,
  ADDR_FROM ,
  MESS    ,
  PUID    ,
  COUNT1  , EVENTDATE
      
  ) VALUES (
          ID1,
  USER_ID1    ,
  ADDR_TO1    ,
  ADDR_FROM1  ,
  MESS1       ,
  PUID1       ,
  COUNT12  , SYSTIMESTAMP
    
    );
    
   -- SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID1;
END  ADD_HISTORY_NOTE;
/


DROP FUNCTION RABAEV.RRL_SHOW_PRICE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SHOW_PRICE( tt_id int )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
   
   select    price
   into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;

   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SHOW_PRICE;
/


DROP FUNCTION RABAEV.RRL_SET_SBORKA_ZONE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_SBORKA_ZONE(
    PALLET_UID1 varchar2  ,
    ZONE1 varchar2 ,
    user_id1 varchar2
) return int
IS
ttt number;
money1 number;
exp_group varchar2(20);
exp_cell varchar2(20);
prov1 int;

BEGIN
 

-- ЗАПОМИНАЕМ ЗОНУ, ИЗ КОТОРОЙ ПЕРЕМЕЩАЛСЯ ПАЛЛЕТ.
  select  ZONE into exp_cell  from  RABAEV.RRL_SBORKA_PALLETS  where PALLET_UID=PALLET_UID1  ; 
    
    if ( (exp_cell is null) or ( exp_cell='' ) ) then
        
        exp_group:='ZERO';
    else
    
        begin
            select  RRL_CELLS.EXPEDITION_GROUP into exp_group from RRL_CELLS where RRL_CELLS.CELL = exp_cell ;
        exception
            when NO_DATA_FOUND then
                exp_group:='ZERO';
            when OTHERS then
                exp_group:='ZERO';
        end;
        
    end if;


    if ( (exp_group is null) or ( exp_group='' ) ) then
        exp_group:='ZERO';
    end if;



  update RABAEV.RRL_SBORKA_PALLETS set ZONE=ZONE1   where PALLET_UID=PALLET_UID1  ; 
     
  
  insert into  RABAEV.RRL_SBORKA_PALLETS_HISTORY 
  (
    PALLET_UID ,
    USER_ID ,
    ZONE,
    EVENT,
    TIME1
  ) values (
    PALLET_UID1 ,
    user_id1 ,
    ZONE1 , 
    'INTERNAL_MOVE' ,
    SYSTIMESTAMP 
  );
  

  -- ТЕПЕРЬ БИЛЛИНГ: 
  -- ОПЛАТА ЗА БИЛЛИНГ БЕРЕТСЯ ИСХОДЯ ИЗ  [ГРУППЫ ЦЕЛЕВОЙ ЯЧЕЙКИ ЗОНЫ ОТГРУЗКИ ]  И  [ГРУППЫ ПОЛЬЗОВАТЕЛЯ ]   

begin 
    money1:=0;
    
-- СНАЧАЛА ПОЙМЕМ В КАКОЙ ГРУППЕ ЯЧЕЕК ЭКСПЕДИЦИИ НАХОДИТСЯ СОБРАННЫЙ ПАЛЛЕТ



    select min(RRL_BILLING_NASTR_INTMOV.UE) into money1 from RUSERS , RRL_CELLS , RRL_BILLING_NASTR_INTMOV
    where RUSERS.ID = user_id1 and RRL_CELLS.CELL = ZONE1 and
    RRL_BILLING_NASTR_INTMOV.EXPEDIT_GROUP_TO = RRL_CELLS.EXPEDITION_GROUP and
    RRL_BILLING_NASTR_INTMOV.USER_GROUP= RUSERS.USER_GROUP  and
    RRL_BILLING_NASTR_INTMOV.EXPEDIT_GROUP_FROM = exp_group ;

prov1:=0;
select count(PALLET_UID ) into prov1 from RRL_BILLING where CELL_TO=ZONE1 and OPERATION='INT_MOVE'  and   PALLET_UID =  PALLET_UID1 ;

      
if ( ( money1>0 ) and (prov1=0) ) then -- ПИШЕМ В ТАБЛИЦУ БИЛЛИНГА

-- Проверка = если есть записи биллинга с той-же CELL_TO , то писать в биллинг не будем. 



insert into RRL_BILLING 
(
     ID           ,
      USER_ID     ,
      UE          ,
      TIMEOF      ,
      OPERATION   ,
      PRIM        ,
      PALLET_UID  
       , CELL_FROM , CELL_TO
) values
(
    RRL_BILLING_SEQ.NEXTVAL ,
    user_id1 , 
    money1 ,
    systimestamp ,
    'INT_MOVE' ,
    '' , 
    PALLET_UID1  , exp_cell , ZONE1
    
) ;





end if;

exception

       when NO_DATA_FOUND then 
           return 0;
        when others then 
           return 0;

end ;

  
return 0;    
END  RRL_SET_SBORKA_ZONE;
/


DROP FUNCTION RABAEV.RRL_GET_PAL_INFOTEXT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_PAL_INFOTEXT(
    PALLET_UID1 varchar2  
) return varchar2
IS
 
addr1 varchar2(50);
prooved1 int;
prooved_by_scan1 int;
zone1 varchar2(200);
trans1 varchar2(200) ;
dock1 varchar2(200);
wave1 varchar2(200); 
ret varchar2(2024);

BEGIN

ret:='';
select P1.ADDR , P1.PROOVED , P1.PROOVED_BY_SCAN ,  TT1.DOCK , P1.ZONE , TT1.TRANSPORT , TT1.WAVE
into  addr1 , prooved1 , prooved_by_scan1 , dock1 , zone1 , trans1 ,  wave1 
  from  RABAEV.RRL_SBORKA_PALLETS  P1 , RRL_TRANSPORT_TASK TT1  where  P1.TRANSTASK_ID = TT1.ID (+) and  PALLET_UID=PALLET_UID1  ; 


ret := concat(  concat( ret , 'ЗОНА:' ) , zone1 ); 
ret := concat(  concat( ret , ' ВРЕМЯ:' ) , wave1 ); 
ret := concat(  concat( ret , ' ДОК:' ) , dock1 ); 
ret := concat(  concat( ret , ' ТРАН:' ) , trans1 ); 

--ret := concat(  concat( ret , '   АДРЕС=' ) , addr1 );




return  ret;
exception
when NO_DATA_FOUND then
    return '';
    when others then 
    return '';
    
END  RRL_GET_PAL_INFOTEXT;
/


DROP FUNCTION RABAEV.ADD_RRL_VOD;

CREATE OR REPLACE FUNCTION RABAEV.ADD_RRL_VOD(
 ID1              INTEGER   ,
  F1               VARCHAR2 ,
  I1               VARCHAR2 ,
  O1               VARCHAR2 ,
  DELETED1         INTEGER  ,
  SOBSTVENNYY1     INTEGER  ,
  PASSPORT1        VARCHAR2 ,
  DOVERENNOST_OT1  VARCHAR2 ,
  TRANSPORT_NUM1   VARCHAR2 ,
  ADDR1            VARCHAR2 ,
  TEL1             VARCHAR2

)
 RETURN INT 
 
 IS
    tmpVar int;
BEGIN
   tmpVar := 0;
   
   begin
   
    select ID into tmpVar from  RABAEV.RRL_TR_VODITEL  where ID=  ID1 ;
    
    update  RABAEV.RRL_TR_VODITEL 
    set 
      F=F1                ,
      I=I1                ,
      O=O1                ,
      DELETED=DELETED1           ,
      SOBSTVENNYY=SOBSTVENNYY1       ,
      PASSPORT=PASSPORT1         ,
      DOVERENNOST_OT=DOVERENNOST_OT1   ,
      TRANSPORT_NUM=TRANSPORT_NUM1    ,
      ADDR=ADDR1             ,
      TEL=TEL1   
        where ID=ID1;
                            
    return tmpVar;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
            SELECT RABAEV.RRL_TR_VODITEL_SQ.NextVal INTO tmpVar FROM DUAL;
            insert into  RABAEV.RRL_TR_VODITEL 
            (
                  ID                 ,
                  F                ,
                  I                ,
                  O                ,
                  DELETED           ,
                  SOBSTVENNYY       ,
                  PASSPORT         ,
                  DOVERENNOST_OT   ,
                  TRANSPORT_NUM    ,
                  ADDR             ,
                  TEL             
            )
            values 
            (
                  tmpVar                 ,
                  F1                ,
                  I1                ,
                  O1                ,
                  DELETED1           ,
                  SOBSTVENNYY1       ,
                  PASSPORT1         ,
                  DOVERENNOST_OT1   ,
                  TRANSPORT_NUM1    ,
                  ADDR1             ,
                  TEL1  
            );
            
           return tmpVar;
       end;

     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
       
commit;
   RETURN tmpVar;  
END ADD_RRL_VOD;
/


DROP FUNCTION RABAEV.RRL_TT_VODITEL_INFO;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_VODITEL_INFO( VODITEL_ID1 int )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select concat( concat( concat( concat( F , ' ' ) , I ) , ' ' ) , O ) into tmpVar from RABAEV.RRL_TR_VODITEL where  ID = VODITEL_ID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VODITEL_INFO;
/


DROP FUNCTION RABAEV.RRL_UPDATE_PALLET_ROW;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_PALLET_ROW( 
    articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2 
 )
 
 RETURN varchar2 
 IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;

BEGIN
    
 select  TAREWEIGHT , ORDER_WEIGHT , TARESIZE , quantity , ORIGINAL_ORDER_WEIGHT , original_quantity
 into   TAREWEIGHT1 , ORDER_WEIGHT1 , TARESIZE1 , quantity1 , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
 from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 if(quantity1=0) then
 
     if( ORIGINAL_ORDER_WEIGHT1 >0 ) then
     
      koef := count1 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1
        ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
        where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
         
        
     end if;
  
 return 'ok';
 else
    
    koef := count1 / quantity1 ;
    
 end if;
 
 

 

 
   update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1
    ,ORDER_WEIGHT= round( ORDER_WEIGHT*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
    where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   

   RETURN 'ok';
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PALLET_ROW;
/


DROP FUNCTION RABAEV.RRL_COUNT_KOR2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_COUNT_KOR2 (
    ART varchar2  ,
    count1 int ,
     CURRENT_MOD_ID2 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
BEGIN




    if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
        

            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
        
    else    

                select    round ( count1/  MS.SHT_IN_KOR ,0 )    into  ttt
                from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
                
                return ttt;
                
           
    end if;

-- =============================================================================

return ttt;
exception
when NO_DATA_FOUND then
            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
    when others then 
    return 0;
END  RRL_COUNT_KOR2;
/


DROP FUNCTION RABAEV.RRL_PALLET_HAS_MODS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PALLET_HAS_MODS(
    PALLET_UID1  varchar2 
 )
 
 RETURN int IS 
tmpVar number;
BEGIN

   tmpVar := 0;
  

select count(  MODS.ID )  into tmpVar 
from   RABAEV.RRL_SBORKA_PALLET_ROWS R , RRL_ARTICUL_MODS MODS
     where    PALLET_UID =   PALLET_UID1  and R.ARTICUL = MODS.ARTICUL and R.CURRENT_MOD_ID = MODS.ID and MODS.DELETED<>1 ; 


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PALLET_HAS_MODS;
/


DROP FUNCTION RABAEV.RRL_OP_WEIGHT2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_OP_WEIGHT2( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;
-- ВЕС ПАЛЛЕТА С УЧЕТОМ ВЕСА ТАРЫ для УКАЗАННОЙ ФАСОВКИ ТОВАРА

BEGIN
   tmpVar := 0;
select sum(  R.ORDER_WEIGHT + RRL_CARTON_WEIGHT2( R.ARTICUL , R.QUANTITY , R.CURRENT_MOD_ID )  )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    R.PALLET_UID = PALLET_UID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_OP_WEIGHT2;
/


DROP FUNCTION RABAEV.RRL_TRASPORT_TASK_UPDATE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TRASPORT_TASK_UPDATE (
    TT_ID    int ,
    TRANSTYPE1 varchar2 , 
    TRANSPORT1 varchar2 ,
    ROUTETYPE1 varchar2 ,
    WAVE1 varchar2 ,
    SHIPMENT_DATE1 DATE , 
    VODITEL_ID1   INTEGER ,
    PRIMECHANIE1 varchar2 ,
    DOCK1 varchar2 , 
    user_id1 varchar2
    
) return int
IS
ID1 int;
BEGIN

   

    update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 , WAVE = WAVE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    return  TT_ID ;

END  RRL_TRASPORT_TASK_UPDATE ;
/


DROP FUNCTION RABAEV.RRL_SBORKA_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_CELL( 
articul1 varchar2 ,
ware_id int , 
count1 number ,
addr1 varchar2
 )
RETURN varchar2
 IS 
-- ФУНКЦИЯ ВОЗВРАЩАЕТ ЯЧЕЙКУ ОТБОРА ДЛЯ АРТИКУЛА, в зависимости от склада , количества и адреса. 
ret1 varchar2(255);
BEGIN
    
    select aa.CELL into ret1 from rrl_articuls aa where aa.ACTICUL = articul1 ;
    
    
    
    return ret1;
exception
when no_data_found then return '';
    when others then
    return '';
END RRL_SBORKA_CELL;
/


DROP FUNCTION RABAEV.RRL_DAY_DISTRIBUTE_ENDS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_DAY_DISTRIBUTE_ENDS
(
    articul1 varchar2 ,
    exp_date1 date 
  
)
 RETURN Date IS
-- Возвращает 1, если товар уже нельзя распределять.

tmpVar varchar(1250);
days_left interval day(5) TO SECOND;
days_left1 number;
days_best_before number;
perc1 number ;
perc2 int;
final_day     Date;                                                                          
             ware_id1 int ;                                                                    
BEGIN


ware_id1:=3;

begin 
-- По артикулу определяем склад
    select  rrl_cells.WARE_ID into ware_id1 from rrl_articuls , rrl_cells where rrl_cells.CELL = rrl_articuls.CELL and rrl_articuls.acticul = articul1 ;
exception   
            when no_data_found then null;
            when others then null;
end;


    tmpVar := '';
    select rrl_articuls.BESTBEFOREDAYS into days_best_before from rrl_articuls where acticul =  articul1                  ;
    days_left :=    (  exp_date1 - SYSTIMESTAMP ) ;
    days_left1:= extract( day from ( days_left  ) )  ;
    
    
-- Пробуем найти настройки срока годности в таблице RABAEV.RRL_WARE_DISTR_TIME_PARAM

begin 
select PP.DISTR_PERC into perc1 from     RABAEV.RRL_WARE_DISTR_TIME_PARAM PP where 
    PP.WARE_ID = ware_id1 and ( days_best_before<=PP.TIME_PERC_TO ) and ( days_best_before > PP.TIME_PERC_FROM ) and ROWNUM<=1;
exception when no_data_found then perc1:=33.33;
    
end ;
    
/*
if( ware_id1=7 or ware_id1=5 ) then
    if( days_best_before<=0 ) then 
        return null;
    end if;
     perc1 := 20;
    -- perc1 = days_left1 / days_best_before;
    if(  days_left1<=20   ) then 
        perc1 := 60;
    else    
        if(  days_left1<=40   ) then 
            perc1 := 50;
        else 
            if(  days_left1<=60   ) then 
                perc1 := 30;
            else
                perc1:=20;
            end if;   
        end if;  
    end if;
 -- Если остаточный срок годности менее   текущая дата + perc*days_best_before , то товар распределять нельзя.


else
    perc1:=33.33;
end if;
*/
 

 DBMS_OUTPUT.put_line( 'exp_date1 =' );
 DBMS_OUTPUT.put_line( exp_date1  );


 DBMS_OUTPUT.put_line( 'days_best_before =' );
 DBMS_OUTPUT.put_line( days_best_before  );

 DBMS_OUTPUT.put_line( 'days_left1 =' );
 DBMS_OUTPUT.put_line( days_left1  );

 DBMS_OUTPUT.put_line( 'perc1=' );
 DBMS_OUTPUT.put_line( perc1 );
 DBMS_OUTPUT.put_line( '--------------------' );

final_day  := exp_date1 -    ( days_best_before*( perc1)/100 );


   RETURN final_day ;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  null ;
     WHEN OTHERS THEN
       RETURN null;
       
END  RRL_DAY_DISTRIBUTE_ENDS;
/


DROP FUNCTION RABAEV.RRL_GET_TT_INFO;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_TT_INFO( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := 'пусто';
   
   select Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) )  into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'пусто';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_INFO;
/


DROP FUNCTION RABAEV.RRL_TRASPORT_TASK_ADD;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TRASPORT_TASK_ADD (
    TRANSTYPE1    VARCHAR2 ,
    SHIPMENT_DATE1 DATE , 
    user_id1 varchar2
) return int
IS
ID1 int;
BEGIN

    SELECT RRL_TRANSPORT_TASK_SQ.Nextval INTO ID1 FROM DUAL;

    insert into    RRL_TRANSPORT_TASK
    (
        ID ,
        CREATEDATE , 
        TRANSTYPE ,
        SHIPMENT_DATE
    ) values (
        ID1 ,
        SYSDATE ,
        TRANSTYPE1 ,
        SHIPMENT_DATE1 
    )    ; 
    
    return ID1;

END  RRL_TRASPORT_TASK_ADD ;
/


DROP FUNCTION RABAEV.RRL_TT_PALLETS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_PALLETS( IDTT int )
 RETURN number IS 
tmpVar int;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
 --    RETURN tmpVar;
-- сначала запросим общее количество паллет
select count(  P.PALLET_UID )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P 
     where  TRANSTASK_ID  = IDTT  ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_PALLETS;
/


DROP FUNCTION RABAEV.RRL_ABC_CALCULATE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ABC_CALCULATE( ware_id1 int  )
    RETURN int IS 
    tmpVar varchar2(255);
    ABC_A1 number;
    ABC_B1 number;
    ABC_XYZ_TIME_EDGES_IN_DAYS1 Numeric;
    Date1 Date;
    Date2 Date;
    
    sum_q number;
    sum_w number;
    sum_s number;
    
    h_sum number;
    
    cursor articul_q
    is 
    select ARTICUL , sum( QUANTITY )  Q
        from RABAEV.RRL_SBORKA_PALLET_ROWS  R ,RABAEV.RRL_SBORKA_PALLETS PP  where ( R.PALLET_UID = PP.PALLET_UID ) 
        and ( PP.CREATE_DATE >= Date1 ) and ( PP.CREATE_DATE <= Date2 ) and ( PP.WARE_ID =  ware_id1 ) 
        group by ARTICUL order by sum( QUANTITY ) DESC  ;

    
BEGIN
-- ФУНКЦИЯ ФОРМИРУЕТ ABC АНАЛИЗ ТОВАРА НА СКЛАДЕ

    Date1:=systimestamp;
    Date2:=systimestamp;

    select  ww.ABC_A , ww.ABC_B, ww.ABC_XYZ_TIME_EDGES_IN_DAYS into ABC_A1 , ABC_B1 , ABC_XYZ_TIME_EDGES_IN_DAYS1 
      from rrl_wares ww where ww.ID = ware_id1; 
     
    Date1:=systimestamp  -    ABC_XYZ_TIME_EDGES_IN_DAYS1 ;
    --DBMS_OUTPUT.put_line(  Date1 );
    --DBMS_OUTPUT.put_line(  Date2 );

    select sum( QUANTITY ) , sum(ORDER_WEIGHT) , sum( R.TARESIZE * ( R.PACK_COUNT ) )   
    into sum_q , sum_w , sum_s
    from RABAEV.RRL_SBORKA_PALLET_ROWS  R ,RABAEV.RRL_SBORKA_PALLETS PP  where ( R.PALLET_UID = PP.PALLET_UID ) 
    and ( PP.CREATE_DATE >= Date1 ) and ( PP.CREATE_DATE <= Date2 ) and ( PP.WARE_ID =  ware_id1 ) ;

    h_sum:=0;
    
    for  art_q in articul_q  loop
      --DBMS_OUTPUT.put_line( h_sum );
        h_sum:=h_sum+art_q.Q;
        update rrl_articuls set SSP= round (art_q.Q/ABC_XYZ_TIME_EDGES_IN_DAYS1 , 0 ) where ACTICUL = art_q.ARTICUL;
        if( ( h_sum / sum_q)>ABC_A1+ ABC_B1  ) then
         --  ГРУППА С
         update rrl_articuls set ABC_GROUP='C' where ACTICUL = art_q.ARTICUL;
         
        else
        
            if( ( h_sum / sum_q)>ABC_A1    ) then
             --  ГРУППА B
                update rrl_articuls set ABC_GROUP='B' where ACTICUL = art_q.ARTICUL;
            else 
            -- ГРУППА С 
                update rrl_articuls set ABC_GROUP='A' where ACTICUL = art_q.ARTICUL;
            end if;
            
        end if;
        --DBMS_OUTPUT.put_line(   art_q.ARTICUL );
    end loop;
  
 --DBMS_OUTPUT.put_line(   'конец' );
 
    RETURN 1;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_ABC_CALCULATE;
/


DROP FUNCTION RABAEV.RRL_PRIHOD_MAY_STORNO;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PRIHOD_MAY_STORNO(
    order_id1  int 
 )
 
 RETURN int IS 
tmpVar number;
BEGIN
-- Проверяем - все-ли паллеты данного прихода находятся в ячейке IN_DOCK

   tmpVar := 0;  

   SELECT count(PP.UID_PALLET) into tmpVar
      FROM RRL_PALLETS PP , RRL_REMAINS REMAINS  where PRIHOD_NAKLAD_ID= order_id1 
    and PP.UID_PALLET = REMAINS.UID_POLETA and REMAINS.CELL<>'IN_DOCK'     ;

if( tmpVar=0 ) then 

    return 1;

else

    return 0;

end if;

   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PRIHOD_MAY_STORNO;
/


DROP FUNCTION RABAEV.RRL_ST_VOLUME;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ST_VOLUME( stnumber1 varchar2 )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where p.ST_NUMBER=stnumber1 and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ST_VOLUME;
/


DROP FUNCTION RABAEV.RRL_GIVE_NEXT_OPALLET_NUMBER;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_NEXT_OPALLET_NUMBER
(
    PREV_PALLET_ID  varchar2 ,
    USER_ID1        varchar2
 )
RETURN varchar2 IS 

    tmpVar varchar2(50);
    ret int;
    ADDR1 varchar2(255) ;
    PALLET_NUMBER1 int;
    PALLET_UID1     VARCHAR2 (100);
    STATE1    VARCHAR2(100) ;
    STDATE1 Date;
    ware_id1 int;
    NAPR1 varchar2(255);
    id2 int;
BEGIN


ret:=0;
select PP.ST_NUMBER , ADDR , STATE , STDATE , ware_id , NAPR into tmpVar , ADDR1 , STATE1 , STDATE1 , ware_id1 , NAPR1 
  from RRL_SBORKA_PALLETS PP where PP.PALLET_UID=PREV_PALLET_ID;
select (max(PALLET_NUMBER )+1) into  PALLET_NUMBER1  from RRL_SBORKA_PALLETS PP where  PP.ST_NUMBER = tmpVar ;

PALLET_UID1:= Concat( 'OP_' , Concat( Concat( tmpVar , '_'  ) ,  PALLET_NUMBER1  ) );


id2 := RABAEV.RRL_SBORKA_PALLETS_ADD2 (
    tmpVar,
    ADDR1 ,
    PALLET_NUMBER1  ,
    PALLET_UID1      ,
    STATE1     ,
    STDATE1  ,
    NAPR1  ,
    USER_ID1  ,
    ware_id1 );




RETURN PALLET_UID1;



   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GIVE_NEXT_OPALLET_NUMBER;
/


DROP FUNCTION RABAEV.RRL_DELETE_OPALLET;

CREATE OR REPLACE FUNCTION RABAEV.RRL_DELETE_OPALLET(
    PALLET_ID1 varchar2 
)
 RETURN varchar2 IS

tmpVar varchar2(250);
iii int;

BEGIN

    select count(ID) into iii from RRL_SBORKA_PALLET_ROWS R where R.PALLET_UID = PALLET_ID1;
    if(iii>0) then
        return 'not_empty';
    else
        delete from  RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1 ;
    end if;
    
RETURN 'ok';
END RRL_DELETE_OPALLET;
/


DROP FUNCTION RABAEV.RRL_CLOSE_OTHOD_PALLET;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLOSE_OTHOD_PALLET
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    PALLET_ID1 varchar2 ,
    iser_id21 varchar2 
)

 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);
PALLET_ROW_ID1 int;

cursor rowss is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 ;

--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS , RABAEV.RRL_PALLETS  
     
    where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and
     RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  
     order by RRL_PALLETS.EXPIRY_DATE  ; 


BEGIN

 
DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar from RABAEV.RRL_SBORKA_PALLETs where PALLET_UID = PALLET_ID1;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;

/*
При закрытии отгрузочной паллеты:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на строку паллета в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


for naklad_row in rowss loop


PALLET_ROW_ID1:= naklad_row.ID;

tmpVar:=0;
kolvo_otbora:=naklad_row.QUANTITY;




   DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ПАЛЛЕТЫ ОТГРУЗКИ!' );
   DBMS_OUTPUT.put_line(  naklad_row.ARTICUL );

    select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;
    
    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );
    DBMS_OUTPUT.put_line(  current_cell );
    

    for  ddd8 in rests_in_cell loop
-- REMAIN
    
        update RABAEV.RRL_SBORKA_PALLET_ROWS set PRIHOD_PALLET_UID = ddd8.UID_POLETA where ID = naklad_row.ID ; 
        update RABAEV.RRL_SBORKA_PALLET_ROWS set EXPIRY_DATE = ddd8.EXPIRY_DATE where ID = naklad_row.ID ; 
        
    
        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );
        DBMS_OUTPUT.put_line(  ddd8.REMAIN );
        DBMS_OUTPUT.put_line(  ddd8.EXPIRY_DATE );
        DBMS_OUTPUT.put_line(  ddd8.UID_POLETA );
        DBMS_OUTPUT.put_line(  '  количество отбора1= ' );     
        DBMS_OUTPUT.put_line(  kolvo_otbora );  
          
        
        if(kolvo_otbora>0) then
/*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
        
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла  
*/          DBMS_OUTPUT.put_line(  CONCAT( 'REMAIN = ' , ddd8.REMAIN )  );
            if(kolvo_otbora <= ddd8.REMAIN )  then
               
                
                
                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      3,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
                    kolvo_otbora:=0;
                else
                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id,
                      current_cell, 
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      ddd8.REMAIN ,
                      3,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
                      
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
                
            end if;      

   
        end if;
    end loop;


         DBMS_OUTPUT.put_line(  '  почти конец ' );   
         DBMS_OUTPUT.put_line(  '  количество отбора2= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  

--если Количество_отбора > 0 
--    Делаем проводку из ячейки 'excess' на отгрузочную накладную
--Количество_отбора  = 0
--конец если
if(kolvo_otbora >0 )  then
                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      'MINUS',
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      3,
                      'MINUS'   ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
kolvo_otbora:=0;
end if;

   DBMS_OUTPUT.put_line(  '  почти конец ' );   

end loop;

update   RABAEV.RRL_SBORKA_PALLETs  set condition = 2  where   PALLET_UID = PALLET_ID1;




   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   
   RETURN 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_CLOSE_OTHOD_PALLET;
/


DROP FUNCTION RABAEV.RRL_SET_SBORSHIK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_SBORSHIK(
    PALLET_UID1 varchar2  ,
    SBORSHIK1 varchar2
) return int
 
IS
ttt number;
 
BEGIN

 
update RABAEV.RRL_SBORKA_PALLETS set SBORSHIK=SBORSHIK1 where PALLET_UID=PALLET_UID1  ; 


return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SBORSHIK;
/


DROP FUNCTION RABAEV.RRL_PAL_ROW_COUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PAL_ROW_COUNT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select count( R.ID  )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_ROW_COUNT;
/


DROP FUNCTION RABAEV.RRL_ST_ROW_COUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_ST_ROW_COUNT( ST varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select count( R.ID  )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.ST_NUMBER   = ST and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_ST_ROW_COUNT;
/


DROP FUNCTION RABAEV.RRL_SET_KLADOVSHIK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_KLADOVSHIK(
    PALLET_UID1 varchar2  ,
    KLADOVSHIK1 varchar2
) return int
 
IS
ttt number;
 
BEGIN

 
update RABAEV.RRL_SBORKA_PALLETS set KLADOVSHIK=KLADOVSHIK1 where PALLET_UID=PALLET_UID1  ; 


return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_KLADOVSHIK;
/


DROP FUNCTION RABAEV.RRL_SET_SCAN_PROOVE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_SCAN_PROOVE(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2
) return int
 
IS
ttt number;
  SPIS_OTBOR_ON_SCAN_OPALL1 int;
  vhelp2 varchar2(255);
  
BEGIN


    if count_of_errors1=0 then
     update RABAEV.RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ; 
     
     DBMS_OUTPUT.put_line(  'flag1' );
     --  СПИСЫВАЕМ ТОВАР ИЗ ЯЧЕЕК ОТБОРА. настройка= SPIS_OTBOR_ON_SCAN_OPALL
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
     DBMS_OUTPUT.put_line(  'flag2' );

           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    '' );
                DBMS_OUTPUT.put_line(  'flag3' );

         end if;
     -- СПИСАНИЕ ОСТАТКОВ ИЗ ОТБОРА   
          
     
    else
     update RABAEV.RRL_SBORKA_PALLETS set  prim=prim1 , COUNT_OF_ERRORS=count_of_errors1  where PALLET_UID=PALLET_UID1  ; 
    end if;
    

return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SCAN_PROOVE;
/


DROP FUNCTION RABAEV.RRL_TT_REGIONS;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_REGIONS( TTID int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);
tmpVar2 varchar2(1024);
cursor ttu is
select distinct REGION from RABAEV.RRL_SBORKA_PALLETS,  RABAEV.RRL_ADDR  where TRANSTASK_ID=TTID and  RRL_SBORKA_PALLETS.ADDR =RRL_ADDR.ADDR ;


BEGIN

   select  TEMP_REGION  into tmpVar2 from RRL_TRANSPORT_TASK where ID = TTID ;
   if( not ( tmpVar2  is null )) 
    then
    --   DBMS_OUTPUT.put_line(  'ffff' );
     return tmpVar2 ;
   end if;
   

for ttq in ttu loop
tmpVar := concat( tmpVar ,concat( ' ' ,  concat( ttq.REGION , '; '  )));
end loop;
   

--update RABAEV.RRL_TRANSPORT_TASK set TEMP_REGION = tmpVar where ID = TTID ;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 'err2';
       RAISE;
END RRL_TT_REGIONS;
/


DROP FUNCTION RABAEV.RRL_VEHICLE_REIS_COUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_VEHICLE_REIS_COUNT( NUM varchar2 , dat Date )
 RETURN int IS 
 varTMP int;
BEGIN
varTMP:=0;
select count(ID) into varTMP from RABAEV.RRL_TRANSPORT_TASK where TRANSPORT=NUM and SHIPMENT_DATE = dat;
   

   
   RETURN varTMP;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 0;
       RAISE;
END RRL_VEHICLE_REIS_COUNT;
/


DROP FUNCTION RABAEV.RRL_BILL_ADD_TTBILL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_BILL_ADD_TTBILL
(
   ID1 int,
   NUM1 varchar2,
   COMPANY1 varchar2,
   DATEOFORDER1 Date,
   DATEFROM1  Date,
   DATETO1  Date ,
   NUM_PLAT1 varchar2
  
   
)
 RETURN int IS
temp_is_closed int;
 aaa int;
                                                              
BEGIN

 
aaa:=0;





 if( ID1>0 ) then
 
 
     select closed into temp_is_closed from RRL_BILL_ORDERS where ID = ID1;
    
    if(temp_is_closed=1) then 
        return ID1;
    end if;
 
 
 -- Обновление?
    update RABAEV.RRL_BILL_ORDERS  set    
      NUM   =NUM1,
      COMPANY   =COMPANY1,
      DATEOFORDER  =DATEOFORDER1,
      DATEFROM     =DATEFROM1,
      DATETO       =DATETO1 ,          
    NUM_PLAT=NUM_PLAT1
    where ID=ID1 ;
 
 
  return ID1;
 
 
 else 
 

   select RRL_BILL_ORDERS_SEQ.NextVal into aaa from dual;
 
 insert into RABAEV.RRL_BILL_ORDERS ( 
  NUM   ,
      COMPANY   ,
      DATEOFORDER  ,
      DATEFROM     ,
      DATETO       ,
      ID , NUM_PLAT
 ) 
 values 
 ( 
    NUM1 , COMPANY1 , DATEOFORDER1 , DATEFROM1 , DATETO1 , aaa , NUM_PLAT1
  );
 
    return aaa;
 
 end if;

 

   RETURN 0;
 
END  RRL_BILL_ADD_TTBILL;
/


DROP FUNCTION RABAEV.RRL_SET_TRANSPORT_PRICE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_TRANSPORT_PRICE(
    PRICE_NAME1 varchar2  ,
    PATH_NAME1 varchar2 ,
    PRICE2 number , 
    kilometers1 number,
    price_hours1 number,
    PRICE2_ADDR number ,
    hours_normative1 number ,
    
    COMPANY2 VARCHAR2
) return int
 
IS
ttt number;
PRICE1 number; 
ID1 int;
path3 varchar2(1024) ;
COMPANY3 varchar(255);

BEGIN

    if( COMPANY2 is null ) then 
        COMPANY3 := '';
    else
        COMPANY3 := COMPANY2;
    end if;

 
DBMS_OUTPUT.put_line(  'begin funct' );

    begin
        
        select path1 into path3 from rrl_tt_path where path1=PATH_NAME1 ; 
        update rrl_tt_path set  path1 = path_name1 , range1 = kilometers1 , NORMATIVE_HOURS = hours_normative1  where  path1=PATH_NAME1  ;
        
    exception when no_data_found then 
        insert into rrl_tt_path  ( path1 , range1 ,  NORMATIVE_HOURS  ) values ( PATH_NAME1 , kilometers1 ,  hours_normative1 );
        when others then null;
    end;






select ID into ID1 from RRL_TRANSPORT_PRICE PR where  PRICE_NAME = PRICE_NAME1 and COMPANY=COMPANY3 ; 

update RRL_TRANSPORT_PRICE set  PRICE = PRICE2 , RANGE1=kilometers1 , PRICE_FOR_HOURS=price_hours1 , PRICE_FOR_ADDR =  PRICE2_ADDR , 
NORM_HOURS = hours_normative1
    where  ID = ID1 ;       
   --   PRICE_NAME = PRICE_NAME1 and ( (COMPANY=COMPANY2) 
   --   or ( ((COMPANY2='') or (COMPANY2 is null)) and ((COMPANY='') or (COMPANY is null))  ) ) ; 

DBMS_OUTPUT.put_line(  'update' );



return 0;
exception
when NO_DATA_FOUND then


    SELECT RRL_TRANSPORT_PRICE_ID.Nextval INTO ID1 FROM DUAL;
    
    insert into RRL_TRANSPORT_PRICE (ID , PRICE_NAME , PRICE ,RANGE1 , COMPANY , PRICE_FOR_HOURS , PRICE_FOR_ADDR , NORM_HOURS ) values 
    ( ID1 ,PRICE_NAME1 , PRICE2 , kilometers1 , COMPANY2 , price_hours1 , PRICE2_ADDR ,  hours_normative1 ) ;
DBMS_OUTPUT.put_line(  'insert' );

    return ID1;
    when others then 
    return -1;
    
END  RRL_SET_TRANSPORT_PRICE;
/


DROP FUNCTION RABAEV.UPDATE_RRL_MOD2;

CREATE OR REPLACE FUNCTION RABAEV.UPDATE_RRL_MOD2 (

  ID1             INTEGER,
  ARTICUL1        VARCHAR2,
  NAME1           VARCHAR2,
  SHT_IN_KOR1     number,
  SHT_WEIGHT1     NUMBER,
  KARTON_WEIGHT1  NUMBER,
  DELETED1        INTEGER
  
) return int
IS
ID2 int;

BEGIN
  

if ID1>0 then

    update  RABAEV.RRL_ARTICUL_MODS
    set 
      ID             = ID1,
      ARTICUL        = ARTICUL1,
      NAME           = NAME1,
      SHT_IN_KOR     = SHT_IN_KOR1 ,
      SHT_WEIGHT     = SHT_WEIGHT1 ,
      KARTON_WEIGHT  = KARTON_WEIGHT1,
      DELETED        =DELETED1
    where ID=ID1;
return ID1;
else

      INSERT INTO RABAEV.RRL_ARTICUL_MODS(
          ID , 
          ARTICUL        ,
          NAME           ,
          SHT_IN_KOR     ,
          SHT_WEIGHT     ,
          KARTON_WEIGHT  ,
          DELETED        
      ) VALUES (
          RABAEV.MODS_SEQ.NEXTVAL,
          ARTICUL1      ,
          NAME1          ,
          SHT_IN_KOR1     ,
          SHT_WEIGHT1     ,
          KARTON_WEIGHT1  ,
          DELETED1                      
        );
        
    SELECT MODS_SEQ.CURRVAL INTO ID2 FROM DUAL;
    
end if;
    
    return ID2;
    
END  UPDATE_RRL_MOD2;
/


DROP FUNCTION RABAEV.RRL_UPDATE_SG;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_SG
(
    articul1 varchar2 ,
   sg int
)
 RETURN int IS

 
                                                              
BEGIN


 update rrl_articuls R set R.BESTBEFOREDAYS=sg where R.ACTICUL=articul1;

   RETURN 0;
 
END  RRL_UPDATE_SG;
/


DROP FUNCTION RABAEV.RRL_TT_POGRESHNOST;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_POGRESHNOST( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN

   tmpVar := 3.5;


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
       
END RRL_TT_POGRESHNOST;
/


DROP FUNCTION RABAEV.RRL_PALLET_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PALLET_WEIGHT(PALID varchar2  )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN

select sum(  R.ORDER_WEIGHT )  into tmpVar from  RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  R.PALLET_UID   = PALID    ;
 
   RETURN tmpVar;

 
 
 
   

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PALLET_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_GIVE_PREVIOUS_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_PREVIOUS_CELL
(
    cell1 varchar2
)

 RETURN varchar2
  IS
tmpVar varchar2(50);
Y1 int ;
X1 int;
Z1 int ;
ware_id1 int ;

BEGIN

select  ware_id ,Y , X , Z into  ware_id1 , Y1 , X1 ,Z1 from RABAEV.RRL_CELLS where CELL = cell1 and BLOCKED_FOR_REMAINS=0 ;

select cell into tmpVar  from
 (select cell 
 from RABAEV.RRL_CELLS where  Z=Z1 and Y=Y1 and X<X1 and ware_id=ware_id1
  order by X DESC )  where  ROWNUM <=1  ;



   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return 'no prev';
     WHEN OTHERS THEN
           return 'err66';
       RAISE;
       
END RRL_GIVE_PREVIOUS_CELL;
/


DROP FUNCTION RABAEV.INT2BOOL;

CREATE OR REPLACE FUNCTION RABAEV.int2bool( 
par int
 )
 RETURN varchar2 
 IS 
 

BEGIN
    

if( par<=0 ) then

   RETURN 'false';
   
end if;

return 'true';

END int2bool;
/


DROP FUNCTION RABAEV.FTIME_SHIPPING_PLAN;

CREATE OR REPLACE FUNCTION RABAEV.ftime_shipping_plan( 
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


DROP FUNCTION RABAEV.RRL_CLEAR_OTBOR_CELL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_CLEAR_OTBOR_CELL(
    CELL1 varchar2 ,
    user_id1 varchar2
)
 RETURN varchar2 IS

tmpVar varchar2(250);
iii int;
otbor1 int;
first1 int;
new_event_uid int;
cursor rests is 
select UID_POLETA , REMAIN from(
select rm.UID_POLETA , rm.REMAIN from rrl_remains rm , rrl_pallets pp where rm.UID_POLETA=pp.UID_PALLET and rm.CELL=CELL1 order by pp.EXPIRY_DATE desc
)  ;

BEGIN

begin
first1:=1;
select otbor into otbor1 from rrl_cells where  cell=CELL1;
    exception when no_data_found  then return 'Такой ячейки нет';
end;

if( otbor1<>1  ) then 
    return 'Ячейка не является ячейкой отбора';
end if;

-- Для всех паллет из ячейки отбора , кроме паллета с самым большим сроком годности, спысываем остаток.
for rest in rests loop
DBMS_OUTPUT.put_line(  'flag1' );
    if( first1<>1 ) then
    
     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
     
        insert into rrl_events ( date_event ,  id_event ,  CELL_FROM   ,
          CELL_TO     ,
          COUNT_EVENT  ,
          TYPE_EVENT   ,
          UID_POLETA   ,
          USER_ID   ) values ( SYSTIMESTAMP , new_event_uid ,  cell1 , 'none' , rest.REMAIN , 3 , rest.UID_POLETA , user_id1 );
DBMS_OUTPUT.put_line(  'flag2' );

    end if;
    first1:=0;
DBMS_OUTPUT.put_line(  'flag3' );

end loop;



    
RETURN 'ok';

exception when no_data_found then return 'нет данных';
--when others then return 'ошибка2';

END  RRL_CLEAR_OTBOR_CELL;
/


DROP FUNCTION RABAEV.RRL_TT_PLAN_SHIPPPING_HOUR;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_PLAN_SHIPPPING_HOUR
( IDTT int )
RETURN timestamp 
IS 
  data_otgruzki timestamp ; 
BEGIN
 
--return systimestamp;
--DBMS_OUTPUT.put_line(  'hello1' );

    select max(  ftime_shipping_plan(  PAL.STDATE , ADR.SHIPPING_TIME ) ) into   data_otgruzki   
      from RRL_SBORKA_PALLETS PAL ,  RRL_ADDR ADR  where  TRANSTASK_ID  = IDTT  and PAL.ADDR=ADR.ADDR(+) ;
      
    DBMS_OUTPUT.put_line(  data_otgruzki );  
      
    update   RRL_TRANSPORT_TASK TT set SHIPMENT_TIME =  data_otgruzki where  TT.ID = IDTT ;


--DBMS_OUTPUT.put_line(  'hello2' );


   RETURN  data_otgruzki;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN null;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN null;
END RRL_TT_PLAN_SHIPPPING_HOUR;
/


DROP FUNCTION RABAEV.RRL_AUTH;

CREATE OR REPLACE FUNCTION RABAEV.RRL_AUTH
(
    login varchar2 , 
    pass1 varchar2
)
 RETURN int
  IS
tmpVar int;


BEGIN


           return -1;
select  ware_id into tmpVar  from RABAEV.RUSERS where ID = login and  PASS = pass1 and  DELETED=0 and PRAVO_ADMIN_LOGIN=1;




   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_AUTH;
/


DROP FUNCTION RABAEV.RRL_GET_USER_INFO;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_USER_INFO( USER_ID1 varchar2 )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := '';
  

select Name into tmpVar from RABAEV.RUSERS where  ID = USER_ID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_USER_INFO;
/


DROP FUNCTION RABAEV.RRL_SBORKA_PLANNINGTIME;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SBORKA_PLANNINGTIME( pall_id1 varchar2 )
 RETURN Date IS 
tmpVar Date;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := null;
  

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN null;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SBORKA_PLANNINGTIME;
/


DROP FUNCTION RABAEV.RRL_DELETE_ST;

CREATE OR REPLACE FUNCTION RABAEV.RRL_DELETE_ST(
ST_NUMBER1 varchar2 
)
 RETURN varchar2 IS
tmpVar varchar2(250);

cursor pallets is select PALLET_UID from RRL_SBORKA_PALLETS where ST_NUMBER  like concat( ST_NUMBER1 , '%' ) ;--and ( ( TRANSTASK_ID=0 )  or ( TRANSTASK_ID is null ) ) 


BEGIN




for roww in pallets loop

   DBMS_OUTPUT.put_line(   roww.PALLET_UID  );
   delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID= roww.PALLET_UID ;
        
end loop;


delete from  RRL_SBORKA_PALLETS where ST_NUMBER like concat( ST_NUMBER1 , '%' ) ; -- and ( ( TRANSTASK_ID=0 )  or ( TRANSTASK_ID is null ) ) ;

 RETURN 'ok';
   
  
END RRL_DELETE_ST;
/


DROP FUNCTION RABAEV.RRL_UPDATE_OTHOD_PALLET_ROWS2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_OTHOD_PALLET_ROWS2(

PALLET_UID_to varchar ,
row_id_from int 


)
 RETURN INT 
 IS
 
tmpVar int;
 
BEGIN
   tmpVar := 0;
 
   
  
      


   
   RETURN tmpVar;
    
END RRL_UPDATE_OTHOD_NAKLAD_ROWS2;
/


DROP FUNCTION RABAEV.RRL_SKLADNAME_BY_ID;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SKLADNAME_BY_ID( ids int )
 RETURN varchar2  IS 
tmpVar varchar2(50);


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select NAME into tmpVar from RABAEV.RRL_WARES W  
     where W.ID = ids  ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ИЗВЕСТНЫЙ СКЛАД';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SKLADNAME_BY_ID;
/


DROP FUNCTION RABAEV.RRL_PRIEMPALLET_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PRIEMPALLET_WEIGHT( pallet_uid varchar2 , count_of number )
 RETURN number IS 
WEIGHT1 number;
itogo int;
sobrano int;
count_of1 number; 
-- Процедура возвращает нормативный вес паллета. Если не указывается количество, для подсчета берется нормативная норма укладки.

BEGIN

    count_of1 :=count_of ;
    WEIGHT1:= 0;

    if( count_of =0 ) then
        select   (ART.NORMA_UKLADKI  /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
        from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
        RETURN WEIGHT1;    
    end if;

    select   (count_of /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
    from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
    RETURN WEIGHT1;   
    
    
     EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PRIEMPALLET_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_PRIEMPALLET_HEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PRIEMPALLET_HEIGHT( pallet_uid varchar2 , count_of number )
 RETURN number IS 
WEIGHT1 number;
itogo int;
sobrano int;
count_of1 number; 
-- Процедура возвращает нормативную высоту паллета. Если не указывается количество, для подсчета берется нормативная норма укладки.

BEGIN

    count_of1 :=count_of ;
    WEIGHT1:= 0;

    if( count_of =0 ) then
        select   (ART.NORMA_UKLADKI  /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
        from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
        RETURN WEIGHT1;    
    end if;

    select   (count_of /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
    from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
    RETURN WEIGHT1;   
    
    
     EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PRIEMPALLET_HEIGHT;
/


DROP FUNCTION RABAEV.RRL_INV_CREATE_LINE3;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INV_CREATE_LINE3
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;

--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end
--==================================================================

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE3;
/


DROP FUNCTION RABAEV.RRL_INV_CREATE_LINE2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INV_CREATE_LINE2
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=1796;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;

--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end
--==================================================================

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE2;
/


DROP FUNCTION RABAEV.RRL_INV_CREATE_LINE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INV_CREATE_LINE
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
BEGIN
price:=1;
NAKLAD_ID:=1796;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );

    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает строчку в плане инвентаризации ( константа ), делая ссылку на адрес.
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

delete from RRL_PRIHOD_NAKLAD_ROWS where INVENT_CELL=cell1 ;

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
        ORDID ,
        ARTICUL ,
        EXPIRY_DATE,
        count1 ,
        price ,
        ID  ,
        INVENT_CELL 
  ) VALUES (
        NAKLAD_ID ,
        articul1 , 
        expiury_date ,
        count1 ,
        price ,
        RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL ,
        cell1
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO id1 FROM DUAL;

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);

 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ


   
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE;
/


DROP FUNCTION RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK
(  
    DOCK1 varchar2 ,  
    time1      timestamp 
)

--  процедура оценивает занятость дока на текущий момент времени. ( Ищет занятые подзоны , смотрим по рейсам ) 
--  Возвращает количество минут после последней спланированной  отгрузки. 
--  Или 0, если док на данное время занят или заняты все его подзоны. 

RETURN number IS
cursor subzones is
 select distinct ZONE from  RABAEV.RRL_TT_ZONES where DOCK=DOCK1 ; 

    max_time timestamp;
    id1 int;
    ret int;
    count_of_pallets  int;
    exist_subzone_with_0_palls int;
    min_palls_in_subzones int;
begin 

    count_of_pallets:=0;
    ret:=0;
    exist_subzone_with_0_palls:=0;
    min_palls_in_subzones:=1000;
    
    DBMS_OUTPUT.put_line( concat( ' Док= ' , DOCK1 ) );
    DBMS_OUTPUT.put_line( 'time1 = ' );
    DBMS_OUTPUT.put_line( time1 );
    -- time1 
    
    begin



        -- Если данный док занят в данный участов времени, то возвращаем 0 
        select TT.ID into id1  from RRL_TRANSPORT_TASK TT , RRL_TT_ZONES ZZ  where TT.DOCK = ZZ.ZONE and ZZ.DOCK= DOCK1 and 
        TT.DOCK_REZERV_TIME_FROM <= time1 and  time1<=   TT.DOCK_REZERV_TIME_TO ;
        DBMS_OUTPUT.put_line( 'Док занят' );
        RETURN 0;
        
    exception
        
        
        
      when no_data_found then
      begin
           -- Если не существует свободной подзоны на указанный период времени, то возвращаем 0 
           DBMS_OUTPUT.put_line( 'Док не занят. бежим по всем подзонам для проверки свободного места' );
           
         for subzone in subzones loop
          
              count_of_pallets := RRL_TT_ZONE_EMPTY( time1 , subzone.ZONE ); 
              -- Если количество паллет в данной подзоне = 0 , то считаем данный док свободным.
               if(count_of_pallets=0) then
                exist_subzone_with_0_palls:=1;
               end if;
               
               if( count_of_pallets < min_palls_in_subzones ) then
                min_palls_in_subzones:= count_of_pallets;
               end if;
               
               DBMS_OUTPUT.put_line( concat(  concat(  concat( 'Подзона = ' , subzone.ZONE  ) , ' количество паллет= '  ) , count_of_pallets )  );
               
         end loop;

        if( exist_subzone_with_0_palls=0 ) then 
          DBMS_OUTPUT.put_line( 'Нет пустых зон, док занят' );
            return 0; -- Если не существует не занятых зон - считаем что док занят.    
        end if;
           
           -- Ищем максиальное время занятости дока.
                select max( TT.DOCK_REZERV_TIME_TO ) into max_time from RRL_TRANSPORT_TASK TT, RRL_TT_ZONES ZZ 
                where TT.DOCK = ZZ.ZONE and ZZ.DOCK=DOCK1 and 
                TT.DOCK_REZERV_TIME_FROM <= time1 and  TT.DOCK_REZERV_TIME_TO <= time1   ;
                DBMS_OUTPUT.put_line(  'время простоя дока в минутах составляет = '  );
                if( max_time is null ) then
                DBMS_OUTPUT.put_line( 10000 );
                    return 10000;
                end if;
                
                 ret :=  CALC_TIMESTAMP_DIFF_IN_SECONDS( time1 , max_time )/60 ;
                
                DBMS_OUTPUT.put_line( time1 );
                DBMS_OUTPUT.put_line( max_time );
                DBMS_OUTPUT.put_line( ret );
                DBMS_OUTPUT.put_line( '!' );
                
          RETURN ret;
          
          exception
          when no_data_found then return -2;
          when others then return -3;
          
      end;
    end;



   RETURN 0;
exception

    when no_data_found then  RETURN 0;
    when others then return -1;

END  RRL_TT_ZONE_IS_EMPTY_DOCK;
/


DROP FUNCTION RABAEV.RRL_IS_PALLET_STRICTLY_FAKE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_is_PALLET_strictly_fake( puid varchar2 )
-- ФУНКЦИЯ ПРЕДСКАЗЫВАЕТ КРИВЫЕ ПОДДОНЫ
 RETURN int IS 
tmpVar int;
tmp2 varchar2(255);
BEGIN
   
   -- если паллет с мезонина или сухого склада , и не прошел весовой контроль
   -- и взвешивался  1 раз, либо интервал между взвешиваниями менее 15 минут, поддон считаем ложным.
begin

   select P.PALLET_UID into tmp2 from RRL_SBORKA_PALLETS P  
   where  ( RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'АЛКО'  )) and (  PROOVED=0 )
   and ( P.PALLET_UID = puid ) ;
  -- сколько раз взвешиваля поддон
 
    begin
       -- and ( count( distinct WEIGHT ) =1 )
       -- если поддон взвешивался 1 раз и времени прошло более 15 минут having ( (max(TIME1)  - min(TIME1))*24*60 >10  ) 
       
        select count(  WEIGHT )   into tmpVar 
            from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and (event='WEIGHT_CHECK')  
            group by PALLET_UID having  ( ( sysdate  - min(TIME1)  )*24*60 >=15 )  ;
            
            if( tmpVar=1 ) then 
            return 1;
            end if;
            
        exception 
            when no_data_found then   return 1;
            when others then null;   
    end;


   begin
        select (max(TIME1)  - min(TIME1))*24*60   into tmpVar 
        from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' 
        group by PALLET_UID  having ( (max(TIME1)  - min(TIME1))*24*60 >15  )  ;
        return 0;
        exception
        when no_data_found then null;
        when others then return 3; 
    end;
    
    
       begin
        select (max(TIME1)  - min(TIME1))*24*60   into tmpVar 
        from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' 
        group by PALLET_UID  having ( (max(TIME1)  - min(TIME1))*24*60 >5  )  ;
        return 4;
        exception
        when no_data_found then return 2;
        when others then return 3; 
    end;
    
    return 0;
exception 
when no_data_found then
    return 0;    
end;

   tmpVar := 0;
   RETURN tmpVar;
END RRL_is_PALLET_strictly_fake;
/


DROP FUNCTION RABAEV.RRL_GET_TT_PRICE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GET_TT_PRICE  
 ( tt_id int )
 RETURN number IS 
price_id1 varchar2(1024);
company_name varchar2(255);
price1 number;
price_hours number;
hours1 number;
tr_type1 varchar(15);
PRICE_FOR_ADDR1 number;
special_price1 int; -- Рассчет Строго по специальному прайсу
address_premio  int;
BEGIN
price1:=0;
price_hours:=0;
hours1:=0;
special_price1:=0;
address_premio :=0;
tr_type1 := '[]';
select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tr_type1 from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
  

   
   DBMS_OUTPUT.put_line(  tr_type1 ); 
   price_id1 :=  RRL_GET_TT_PRICE_ID( tt_id )  ;
   DBMS_OUTPUT.put_line(  price_id1 ); 
   company_name:='';
   -- Определяем  КОМПАНИЮ 
   begin 
   DBMS_OUTPUT.put_line(  'flag1' ); 
    select   VOD.DOVERENNOST_OT , RRL_TT.HOURS into company_name , hours1  from RRL_TRANSPORT_TASK RRL_TT , RRL_TR_VODITEL VOD
        where   RRL_TT.VODITEL_ID = VOD.ID and RRL_TT.ID = tt_id ;
        -- По собственному транспорту биллинг не ведем
        DBMS_OUTPUT.put_line(  'flag2' ); 
        DBMS_OUTPUT.put_line( concat( 'КОМПАНИЯ=' , company_name ) );
        --if( company_name='МОНЕТКА' ) then 
        --return 0;
        --end if;
        
         select CC.SPECIAL_PRICE into special_price1 from RABAEV.RRL_BILL_COMPANY CC where CC.COMPANYNAME =  company_name ;
        
   exception 
     WHEN NO_DATA_FOUND THEN 
     DBMS_OUTPUT.put_line(  'Не найден водитель, либо рейс. '  );
      return 0;
      wHEN OTHERS THEN  DBMS_OUTPUT.put_line(  ' Неизвестная ошибка '  ); return 0;
   end;
   
   DBMS_OUTPUT.put_line(  company_name  ); 

   if( company_name='' ) then 
   return 0;
   end if;
      
      DBMS_OUTPUT.put_line( 'flag 4' );
      
   begin
   -- СНАЧАЛА ПРОБУЕМ НАЙТИ ПРАЙС СООТВЕТСТВУЮЩИЙ  РАЙОНУ+СОМПАНИИ
    DBMS_OUTPUT.put_line( 'flag 7' );
       
     select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR into price1 , price_hours , PRICE_FOR_ADDR1 from RABAEV.RRL_TRANSPORT_PRICE PR 
     where PR.PRICE_NAME=price_id1 and PR.COMPANY=company_name and rownum<=1 ;
     
     address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))     where ID = tt_id  ;     
     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
           
           
   exception 
        WHEN NO_DATA_FOUND THEN
        begin
        
            DBMS_OUTPUT.put_line( 'flag 3' );
        
            -- ЗАТЕМ ПРОСТО РАЙОНУ 
            select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR  into price1 , price_hours, PRICE_FOR_ADDR1 from RRL_TRANSPORT_PRICE PR 
            where PR.PRICE_NAME=price_id1 and ( PR.COMPANY is null or PR.COMPANY=''  ) and special_price1=0 and rownum<=1 ;
            DBMS_OUTPUT.put_line( price1 );   
            DBMS_OUTPUT.put_line( price1 + hours1 * price_hours );  
            
            address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
            update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
            return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
            
             
        exception
            WHEN NO_DATA_FOUND THEN
            begin
            price_id1 :=  RRL_GET_TT_PRICE_ID2( tt_id )  ;
               DBMS_OUTPUT.put_line(  price_id1 );
             -- ЗАТЕМ РЕГИОНУ+КОМПАНИИ 
                select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR   into price1 , price_hours , PRICE_FOR_ADDR1 
                from RRL_TRANSPORT_PRICE PR where PR.PRICE_NAME=price_id1 and PR.COMPANY=company_name  and rownum<=1  ;
                
                
                address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
                update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                
             -- ЗАТЕМ ПРОСТО РЕГИОНУ.
             exception 
             WHEN NO_DATA_FOUND THEN
                begin
                    select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR   into price1 , price_hours , PRICE_FOR_ADDR1 
                    from RRL_TRANSPORT_PRICE PR where PR.PRICE_NAME=price_id1 and ( PR.COMPANY is null or PR.COMPANY='' ) and special_price1=0
                     and rownum<=1 ;
                  
                     address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
                     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                   
                exception
                WHEN NO_DATA_FOUND THEN
                    --  ТЕПЕРЬ БЕЖИМ ПО СПИСКУ РЕГИОНОВ МАРШРУТА и ПОЛУЧАЕМ МАКСИМАЛЬНУЮ ЦЕНУ ИЗ СПИСКА.
                    
                    begin 
                    DBMS_OUTPUT.put_line( 'flag -1' );
                    select  max( PR.PRICE) , max( PR.PRICE_FOR_HOURS), max( PR.PRICE_FOR_ADDR )  into price1 , price_hours ,  PRICE_FOR_ADDR1  
                    from  RRL_TRANSPORT_PRICE PR ,  (
                    select DISTINCT  Concat (Concat( tr_type1 , upper(ADDR1.REGION) ) , ';')  REGION   from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  
                    where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id ) REG 
                    where PR.PRICE_NAME=REG.REGION and PR.COMPANY=company_name having count(PR.PRICE)>=1
                     ;
                     
                    address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)  )) ;
                    update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))   where ID = tt_id  ;     
                    return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                    
                    exception 
                        WHEN NO_DATA_FOUND THEN
                        begin
                        
                                DBMS_OUTPUT.put_line( 'flag 1' );
                                
                                select  max( PR.PRICE) , max( PR.PRICE_FOR_HOURS) , max( PR.PRICE_FOR_ADDR )  into price1 , price_hours ,  PRICE_FOR_ADDR1   from  RRL_TRANSPORT_PRICE PR ,  (
                                select DISTINCT  Concat (Concat( tr_type1 , upper(ADDR1.REGION) ) , ';')  REGION   from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  
                                where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id ) REG 
                                where PR.PRICE_NAME=REG.REGION and ( PR.COMPANY is null or PR.COMPANY='' ) and special_price1=0
                                 having count(PR.PRICE)>=1 ;
                                  
                               address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)  )) ;
                                update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                                return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                                
                                exception
                                WHEN NO_DATA_FOUND THEN return 0;
                        end;
                        when others then return 0;
                    end;
                    
                    return 0;
                  when others then return 0;  
                    
                end;
             
            end;
        end;
   end;
      
   
   address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )+1)     where ID = tt_id  ;     
     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
     

   RETURN 0;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN -1;
END RRL_GET_TT_PRICE;
/


DROP FUNCTION RABAEV.RRL_TT_ZONE_FIND_EMPTY_PLACE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ZONE_FIND_EMPTY_PLACE
(  
  time1      timestamp, 
  ZONE1  VARCHAR2
)
-- Написать процедуру поиска первого свободного места для ворот (зоны) в данное время. F(Время , Зона   )
-- Ищется как ближайший не занятое паллето-место к зоне, имеющее расстояние не более 1 от зоны , иначе возвращается место OVERFLOW. 

RETURN varchar2 IS

X_min int;
RES_SUBZONE varchar2(255);
RES_DIST number;

begin 


DBMS_OUTPUT.put_line( concat( concat( ' --------------- RRL_TT_ZONE_FIND_EMPTY_PLACE (' , ZONE1  ) , ');' ));


-- Для данной зоны находим минимум по оси Х  
select min(X) into X_min from  RRL_TT_ZONES ZZ where ZZ.ZONE=ZONE1 ; 


-- по всем ячейкам, отстоящим не более чем на 1 позицию по оси Х   находим незанятую ячейку на данное время, 
-- имеющую минимальное расстояние до начала зоны  
select SUB_ZONE , DIST into RES_SUBZONE , RES_DIST  from
 (
    select
    SUB_ZONE , 
    RRL_TT_ZONE_DISTANCE_TO_DOCK(  ZONE1 , SUB_ZONE ) DIST
     from  RRL_TT_ZONES ZZ  where 
        abs( X-X_min) <=1 and 
        (RRL_TT_ZONE_EMPTY( time1 , ZZ.SUB_ZONE  )=0) /* Количество паллет допустимое в ячейке */ 
    order by RRL_TT_ZONE_DISTANCE_TO_DOCK(  ZONE1 , SUB_ZONE )
) where ROWNUM=1
    ;


   RETURN RES_SUBZONE;
exception

    when no_data_found then  RETURN 'ERR1';
    when others then return 'ERR2';

END  RRL_TT_ZONE_FIND_EMPTY_PLACE;
/


DROP FUNCTION RABAEV.RRL_TT_PLAN_PALL_ZONES;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_PLAN_PALL_ZONES
(  
  TT  int , 
  ZONE1 varchar2 , -- Зона 
  time1 timestamp , -- Время плановой отгрузки товара 
  replain int
)


-- Процедура назначения плановых мест для паллетт маршрута. (фиксации занятости )
-- Паллеты маршрута упорядочиваются по: Адресу (согласно планирования логистов) , весу.
    
-- Для каждой паллеты из маршрута определяется свободное место, и фиксируется на 
-- время от ( начала плановой отгрузки товара - 30 минут ) до ( начала плановой отгрузки товара + 30 минут )


RETURN int IS


    cursor aaa is 
    select SP.PALLET_UID , ZONE from RRL_SBORKA_PALLETS SP , RRL_ADDR ADR 
    where SP.TRANSTASK_ID = TT and SP.ADDR = ADR.ADDR order by SP.ORD , RRL_PAL_WEIGHT( SP.PALLET_UID ) desc ; 

    cell1 varchar2(255) ; 

  time2 timestamp;
  time3 timestamp;

begin 

if ( replain=1 ) then 
    
    update RRL_SBORKA_PALLETS  set 
        ZONE=null , 
        ZONE_TIME_PLAN_IN   = null   ,
        ZONE_TIME_PLAN_OUT = null 
    where  TRANSTASK_ID = TT ;
    
end if;
time2 := time1 - 1/24;
time3 := time1 + 1/24;


update RRL_TRANSPORT_TASK set DOCK = ZONE1 , 
DOCK_REZERV_TIME_FROM  = time1 ,
DOCK_REZERV_TIME_TO = time3
 where ID = TT ;


for aa in aaa loop
-- Для каждой паллеты из маршрута определяется свободное место, и фиксируется на 
-- время от ( начала плановой отгрузки товара - 30 минут ) до ( начала плановой отгрузки товара + 30 минут )
    
    cell1 := RRL_TT_ZONE_FIND_EMPTY_PLACE(  time1  ,  ZONE1  );
    update RRL_SBORKA_PALLETS set  
        ZONE=cell1 , 
        ZONE_TIME_PLAN_IN   = time2   ,
        ZONE_TIME_PLAN_OUT = time3 
    where PALLET_UID = aa.PALLET_UID ;
    
    DBMS_OUTPUT.put_line(  concat( 'Зафиксировано место для паллета ' ,  aa.PALLET_UID )  );
    DBMS_OUTPUT.put_line( concat( 'ячейка ' , cell1 )  ) ;  
        
    DBMS_OUTPUT.put_line( time2 );
    DBMS_OUTPUT.put_line( time3 );

end loop;

   RETURN 0;
exception

    when no_data_found then 
    DBMS_OUTPUT.put_line( 'no_data_found' ) ;
     RETURN 0;
    when others then
    DBMS_OUTPUT.put_line( 'others' ) ;
     return 0;

END  RRL_TT_PLAN_PALL_ZONES;
/


DROP FUNCTION RABAEV.RRL_MAY_DISTRIBUTE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_MAY_DISTRIBUTE
(
    articul1 varchar2 ,
    exp_date1 date
)
 RETURN int IS
-- Возвращает 1, если товар уже нельзя распределять.

tmpVar varchar(1250);
days_left interval day(5) TO SECOND;
days_left1 number;
days_best_before number;
perc1 number ;
perc2 int;
ware_id1 int;                                                                                
                  
day_of_distr_end date;
                                                              
BEGIN



day_of_distr_end := RRL_DAY_DISTRIBUTE_ENDS( articul1 , exp_date1   );
if( day_of_distr_end is null ) then 
-- Товар протух 
    return 0;
else 
    
    if( day_of_distr_end> SYSTIMESTAMP  ) then
        return 1;
    end if;
    
end if;



   RETURN 0;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  1 ;
     WHEN OTHERS THEN
       RETURN 1;
END  RRL_MAY_DISTRIBUTE;
/


DROP FUNCTION RABAEV.RRL_SET_SCAN_PROOVE2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_SET_SCAN_PROOVE2(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2 , 
    SBORSHIK1  VARCHAR2,
    KLADOVSHIK1 VARCHAR2
) return int
 
IS
vhelp2 varchar2(255);
ttt number;
 SPIS_OTBOR_ON_SCAN_OPALL1 int;
BEGIN


    if count_of_errors1=0 then
    
     update RABAEV.RRL_SBORKA_PALLETS set    PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ;
     --  СПИСЫВАЕМ ТОВАР ИЗ ЯЧЕЕК ОТБОРА. настройка= SPIS_OTBOR_ON_SCAN_OPALL
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    KLADOVSHIK1 );
         end if;
     -- СПИСАНИЕ ОСТАТКОВ ИЗ ОТБОРА   
          
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
    
END  RRL_SET_SCAN_PROOVE2;
/


DROP FUNCTION RABAEV.RRL_UPDATE_PALLET_ROW2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_PALLET_ROW2( 
    articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2
 )
 
 RETURN varchar2 
 IS 
 
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
        ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
        where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
         
        
     end if;
  

 else
    
    koef := count1 / quantity1 ;
       update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1 ,  VYCHERK_USER_ID = user_id1 
    ,ORDER_WEIGHT= round( ORDER_WEIGHT*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
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
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PALLET_ROW2;
/


DROP FUNCTION RABAEV.RRL_GIVE_DESTINATION_CELL2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_GIVE_DESTINATION_CELL2 (
-- ДАННАЯ ПРОЦЕДУРА ПРЕДЛАГАЕТ ЯЧЕЙКУ ДЛЯ РАЗМЕЩЕНИЯ. ЕСЛИ ТОВАР РАЗМЕЩЕН, УКАЗЫВАЕТ КУДА.
 pallet_uid varchar2 , 
 ware_id1 int
 
 ) return varchar2
is


cell_destination  varchar2(50) ;
tmpVar NUMBER;
PX int; 
PY int;
PZ int;
etaj_limit1 int;
m_RRL_TIME_FOR_RESERV int;
error_name  varchar2(250) ;
articul3  varchar2(250) ;
pallet_weight1 number;
pallet_height1 number;
debug_mode int;
 
cursor ddd is 
select cell from RRL_CELLS where UID_POLETA_FOR_BLOCK = pallet_uid and TIME_FOR_BLOCK >=    SYSTIMESTAMP  ;

cursor pallet_row is 
select * from RRL_PALLETS where UID_PALLET = pallet_uid    ;


cursor cell_for_pick is
select c1.*  from RABAEV.RRL_CELLS c1, RABAEV.RRL_ARTICULS , RABAEV.RRL_PALLETS   where
    RRL_ARTICULS.CELL = C1.CELL and RRL_PALLETS.ARTICUL= RRL_ARTICULS.ACTICUL
    and RRL_PALLETS.UID_PALLET = pallet_uid 
    and (     (( UID_POLETA_FOR_BLOCK is null ) or ( TIME_FOR_BLOCK < SYSTIMESTAMP ))  );


BEGIN

--m_RRL_TIME_FOR_RESERV:=RRL_TIME_FOR_RESERV();
debug_mode:=1;
etaj_limit1:=100;
articul3:='';
pallet_weight1:=RRL_PRIEMPALLET_WEIGHT(pallet_uid  , 0 );
pallet_height1:=RRL_PRIEMPALLET_HEIGHT(pallet_uid  , 0 );

begin

select RRL_PALLETS.ARTICUL into articul3 from RRL_PALLETS where RRL_PALLETS.UID_PALLET = pallet_uid ;
select etaj_limit into etaj_limit1  from rrl_articuls where acticul = articul3;

exception

    WHEN NO_DATA_FOUND THEN
       null;
    WHEN OTHERS THEN
       null;

end;



    if(debug_mode=1) then
        DBMS_OUTPUT.put_line( ' Hello 1 ');
    end if;


error_name:='';
cell_destination:='NONE';
-- Если существует паллето-место, куда указан резерв на данный паллет 
-- (и время ожидания не истекло), выбирается первое паллето-место. 
for fff in  ddd loop
    cell_destination:=fff.cell;
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана ячейка, назначенная раннее ');
            end if;
    return cell_destination;
end loop;

begin
-- ЕСЛИ ДАННЫЙ ПАЛЛЕТ ИМЕЕТ ОСТАТКИ В ЗОНЕ ХРАНЕНИЯ, ВЫДАЕМ ЭТОТ CELL 
    select C.CELL into cell_destination from RABAEV.RRL_REMAINS R , RABAEV.RRL_CELLS C 
        where R.CELL=C.CELL and R.UID_POLETA=pallet_uid 
        and R.REMAIN>0 and C.BLOCKED_FOR_REMAINS=0 and C.BLOCKED_FOR_POPOLNENIE=0 ;

    return cell_destination;
exception
        WHEN NO_DATA_FOUND THEN
        cell_destination:='NONE1';
         WHEN OTHERS THEN
         cell_destination:='NONE2';
end;

--Иначе, выбирается ячеека отбора для данного артикула  , если она с нулевыми (или меньшими)
-- остатками, и на которую нет действующего резерва другого паллета.
for cell_for_pick1 in cell_for_pick loop

PX:=cell_for_pick1.X;
PY:=cell_for_pick1.Y;
PZ:=cell_for_pick1.Z;



--  select sum(REMAIN) into tmpVar from RRL_REMAINS where cell = cell_for_pick1.cell group by cell ;

tmpVar:=RRL_GET_CELL_REMAIN( cell_for_pick1.cell);
    -- определяем остатки в ячейке отбора 

    if( ( (tmpVar) is null) or (tmpVar=0)  ) then
    
        cell_destination:=cell_for_pick1.cell;
        -- ФИКСИРУЕМ РЕЗЕРВ В ТАБЛИЦЕ ЯЧЕЕК 
        update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
        where RRL_CELLS.CELL = cell_for_pick1.cell ;
        
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана свободная ячейка пикинга ');
            end if;
        
        return cell_destination;
    
    end if;
   
end loop;



--Если свободной ячейки отбора нет, среди всех ячеек хранения отбираем свободную 
--не зарезервированную ячейку с наименьшим весом, чтобы не нарушалось ограничение этажа. Вес определяется как расстояние 
--от ячейки отбора данного паллета. 
--Если такой ячейки нет, помещаем паллет в зону переполнения.
--ВЕС: пусть X - ячейки по горизонтали Y - вертикаль  Z  - параллельные ряды.   
-- расстояние между 2-мя ячейками = abs( X1 - X2 ) + 2* abs(Y1-Y2) + 20 * abs(Z1-Z2)




    begin

        select CELL into cell_destination from 
        RRL_CELLS where (BLOCKED_FOR_ACCEPT=0) and (OTBOR=0) and ( ( TIME_FOR_BLOCK is null ) or (TIME_FOR_BLOCK <=    SYSTIMESTAMP )) 
        and RRL_GET_CELL_REMAIN(CELL)=0  and ROWNUM <=1   and ware_id=ware_id1 and Y<=etaj_limit1  and   pallet_weight1<= LIMIT_WEIGHT
        and pallet_height1<=LIMIT_HEIGHT
        order by 4*abs(PX-X)+abs(PY-Y)+40*abs(PZ-Z) , LIMIT_HEIGHT ;
        
        -- фиксируем наш выбор на 12 минут.
        --update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '12' minute
        --where RRL_CELLS.CELL = cell_destination ;

            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Найдена свободная ячейка хранения ');
            end if;

        
    EXCEPTION
         WHEN NO_DATA_FOUND THEN
            cell_destination:='OVERFLOW';
         WHEN OTHERS THEN
            cell_destination:='OVERFLOW2';
    end;



if( (cell_destination<>'OVERFLOW' ) and (cell_destination<>'OVERFLOW2' )  ) then
   update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
   where RRL_CELLS.CELL = cell_destination ;

end if;

   
    if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Результат зафиксирован ');
    end if;  
     

return cell_destination;

end;
/


DROP FUNCTION RABAEV.RRL_INTERNAL_MOVE3;

CREATE OR REPLACE FUNCTION RABAEV.RRL_INTERNAL_MOVE3(
pallet_id varchar2 , 
cell_to varchar2 ,
count1 number ,
user_id1 varchar2
)
-- ПРОЦЕДУРА ВНУТРЕННЕГО ПЕРЕМЕЩЕНИЯ 
-- ЕСЛИ ПЕРЕМЕЩЕНИЕ ИДЕТ В ЯЧЕЙКУ ОТБОРА, ТО КОНТРОЛИРУЕТСЯ 
--  - ЯВЛЯЕТСЯ ЛИ ДАННАЯ ЯЧЕЙКА РОДНОЙ ДЛЯ ДАННОГО ТОВАРА 

RETURN varchar2

IS
count2 number;
tmpVar NUMBER;
tmpVar2 varchar(250);
art1 varchar2(50) ;
is_otbor int;
remain_in_cell_to number;
checks_passed int;
cell_from1 varchar2(50);
cell_next varchar2(150);
dummy1 varchar(500);
dummy2 varchar(500);

articul1 varchar2(250);
cell_otbora_for_pallet varchar2(50);
ware_id_to int;
debug_mode int;
new_event_uid int;
SPIS_IF_HRAN_NO_EMPTY1 varchar(100);
data_spisania Date ;
alternative_puid varchar2(400);
alternative_cell varchar2(400);
alternative_date date;
rret varchar2(500);
helv varchar2(500);

user_group1 varchar2(500);
weight_limit_warning1 int;
WEIGHT_LIMIT_STOP1 int;
weight_of_cell_to number;
PRIEMPALLET_WEIGHT1 number;
prihod_cond int;
cursor rrr is select * from RRL_REMAINS where CELL = cell_to;
cursor rrr2 is select * from  RABAEV.RRL_REMAINS  where CELL=cell_to ;

BEGIN
    

begin
    select rusers.USER_GROUP into user_group1 from rusers where rusers.ID=user_group1 ;
exception 
        when no_data_found then null;
        when others then null;
end;



    begin -- ФИКСИРУЕМ ВРЕМЯ ПОСЛЕДНЕГО ДОСТУПА К ЯЧЕЙКЕ        
        update rrl_cells set LAST_TIME_OF_UPDATE= SYSTIMESTAMP where CELL=cell_to;
    exception        
        when no_data_found then null;
        when others then null;
    end;


select ware_id into ware_id_to from RABAEV.rrl_cells CC where CC.cell =  cell_to;
articul1:=null;

DBMS_OUTPUT.put_line( 'Начало' );

if( pallet_id<>'NO_PALLET' ) then

    begin
        select PA.ARTICUL into articul1 from  RABAEV.RRL_PALLETS  PA where PA.UID_PALLET=pallet_id;
    exception
    when no_data_found then 
        helv:= Concat( 'отсутствует паллет ' , concat( pallet_id , concat( ' ячейка=' , cell_to) ) ) ; 
        insert into rrl_error_log ( error , datet  ,user_id ) values ( helv , systimestamp , user_id1 ) ;
        DBMS_OUTPUT.put_line( 'ошибка 0 типа' );
        return 'Pallet Udalen. I2';
    when others then 
        DBMS_OUTPUT.put_line( 'ошибка 1 типа' );
    end;

end if;

DBMS_OUTPUT.put_line( articul1 );

DBMS_OUTPUT.put_line( 'Флаг1' );


   prihod_cond:=0;
   count2:=count1;
   debug_mode:=0;
   tmpVar := 0;
   is_otbor:=0;
   remain_in_cell_to:=0;
   checks_passed:=0;
   cell_from1:='NONE';
   weight_limit_warning1:=0; -- Настройка - предупреждать - ли в случае превышения веса
   PRIEMPALLET_WEIGHT1 := 0; -- Вес перемещаемого товара
   WEIGHT_LIMIT_STOP1 := 0;



 -- ЕСЛИ списание на НЕДОСТАЧУ
if  ( pallet_id='NO_PALLET' ) then

    begin
        for fgr in rrr  loop
        --
             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );

        --
        end loop;
     exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL;
    
    end;

    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
    RETURN CONCAT('ok_' ,  cell_next );
end if;


-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?
begin
    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;

    if( (prihod_cond=1) or (prihod_cond=0) ) then
        return 'NAKLAD_NE_ZAKRYTA';
    end if;

   exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL; 
    
end;




    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА
    

        select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;
        -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;



        if(count2=0) then
            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
        end if;

    exception
        WHEN NO_DATA_FOUND THEN
        
        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   
        UID_POLETA=pallet_id and cell=cell_to;
         
            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
            RETURN CONCAT('ok_' ,  cell_next );
        

         WHEN OTHERS THEN
            begin
            
                    begin
                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА
                    
                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where
                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;
                         
                    exception
                
                        WHEN NO_DATA_FOUND THEN
                        
                            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'net stolko tovara',  pallet_id ,  count1  ) ;
                            return 'net stolko tovara';
                            
                        WHEN OTHERS THEN
                           null ; -- return 'other pallet3';
                    end;

                         
                    if(count2=0) then
                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
                    end if;
                    


                    
            exception
            
                WHEN NO_DATA_FOUND THEN
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet1',  pallet_id ,  count1  ) ;
                    return 'other pallet1';
                WHEN OTHERS THEN
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet2',  pallet_id ,  count1  ) ;
                    return 'other pallet2';
            end;
         
            
    end;
    

if( cell_to=cell_from1 ) then 
    return 'cell_to=cell_from1';
end if;   
    

    if(count2=0) then
        return 'count2=0';
    end if;





begin
    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 
    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 
    select OTBOR  into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;
exception
         WHEN NO_DATA_FOUND THEN
         
           return 'no_pallet_cell_to';
         WHEN OTHERS THEN
           return 'other pallet1';
end;


if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then

PRIEMPALLET_WEIGHT1 := RRL_PRIEMPALLET_WEIGHT( pallet_id , count1 );
-- Если перемещение идет не в ячейку отбора, проверяем параметры веса ячейки.  если вес не допустим -
-- тогда предупреждение или отказ (в зависимости от настроек склада ячейки, куда перемещается товар)                 
    -- Находим ограничения по весу для данной ячейки.
    begin
    
        select weight_limit_warning , cells.LIMIT_WEIGHT , WEIGHT_LIMIT_STOP into weight_limit_warning1 , weight_of_cell_to , WEIGHT_LIMIT_STOP1 from rrl_wares ww , rrl_cells cells 
            where cells.CELL = cell_to and cells.WARE_ID= ww.ID ;
            -- ЕСЛИ ВКЛЮЧЕНА НАСТРОЙКА СРАВНЕНИЯ ВЕСА И ПРЕДУПРЕЖДЕНИЯ О ВЕСЕ.
            if (  weight_limit_warning1 = 1 ) then  -- СРАВНИВАЕМ ВЕС ПАЛЛЕТА С ЛИМИТАМИ ПО ДАННОЙ ЯЧЕЙКЕ 
               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then
                 dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'weight_limit_warning',  pallet_id ,  count1  ) ;
               end if;
            end if;

            if (  WEIGHT_LIMIT_STOP1 = 1 ) then  
               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then
                return 'LIMIT_VESA';
               end if;
            end if;

            
        exception
        WHEN NO_DATA_FOUND THEN null;
        WHEN OTHERS THEN null;
        
    end; 



-- ЕСЛИ перемещение идет не в назначенную ячейку - сообщение об ошибке  карщика.      




    begin
        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;
    exception
             WHEN NO_DATA_FOUND THEN
               remain_in_cell_to:=0;
             WHEN OTHERS THEN
               remain_in_cell_to:=0;
    end;

    if remain_in_cell_to is null then
    remain_in_cell_to:=0;
    end if;

    if(remain_in_cell_to<=0)  then
        checks_passed:=1;
    else
        -- ЕСЛИ ДЛЯ ДАННОЙ ЯЧЕЙКИ  УЖЕ ЕСТЬ ОСТАТОК ЧЕГО -ТО 
     -- если для данного склкда указана опция - списывать паллеты на недостачу, то списываем все в соотв. ячейку.
        select SPIS_IF_HRAN_NO_EMPTY into SPIS_IF_HRAN_NO_EMPTY1  from rrl_wares where rrl_wares.id = ware_id_to;
        
        if( (not ( SPIS_IF_HRAN_NO_EMPTY1 is null ) ) or (SPIS_IF_HRAN_NO_EMPTY1 <>'')  ) then
        
           
                checks_passed:=1;
                
                 for fgr2 in rrr2  loop
                    
                     tmpVar2:=RABAEV.RRL_INTERNAL_MOVE2(
                     fgr2.UID_POLETA  , 
                     SPIS_IF_HRAN_NO_EMPTY1  ,
                     fgr2.REMAIN ,
                     user_id1 
                        );

                end loop;
                
           
        
        end if;
        
        
        if(checks_passed=0) then
            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'cell_not_empty',  pallet_id ,  count1  ) ;
            return 'cell_not_empty';
        end if;
        
    end if;

else

DBMS_OUTPUT.put_line( 'спуск в отбор' );

    if cell_to<>'MEZONIN' then
        begin
            -- НЕ ДАЕМ СТАВИТЬ ТОВАР В ЛЕВЫЙ ОТБОР
                select AR.CELL , PP.EXPIRY_DATE  into  cell_otbora_for_pallet , data_spisania
                from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_ARTICULS AR   
                where   PP.UID_PALLET = pallet_id and AR.ACTICUL=PP.ARTICUL ;
                
                if( cell_otbora_for_pallet<>cell_to ) then
                    DBMS_OUTPUT.put_line( concat( cell_otbora_for_pallet , concat( '#' , cell_to ) ) );
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'OTBOR_DRUGOGO_ARTICULA',  pallet_id ,  count1  ) ;
                    return 'OTBOR_DRUGOGO_ARTICULA';
                end if;
                
                
                -- Проверяем нарушение принципа FEFO 
                -- ИЩЕМ ПАЛЛЕТ ЭТОГО ТОВАРА В ХРАНЕНИИ ХУДШИМ СРОКОМ 
                -- data_spisania 
                DBMS_OUTPUT.put_line( concat('Флаг2' , articul1 ) );
                if not ( articul1  is null ) then
                DBMS_OUTPUT.put_line( 'ffff4' );
                    if  (1=1) then 
                    
                        alternative_puid :='';
                        alternative_cell :='';
                        alternative_date:=null;
                        begin
                        DBMS_OUTPUT.put_line( 'Флаг3' );
                            select UID_PALLET , CELL , EXPIRY_DATE  into alternative_puid , alternative_cell , alternative_date  from  (
                            select  PA.UID_PALLET , REMA.CELL , PA.EXPIRY_DATE  from RABAEV.RRL_REMAINS REMA , RABAEV.RRL_PALLETS  PA , RRL_CELLS CE  where 
                            REMA.UID_POLETA= PA.UID_PALLET and REMA.CELL=CE.CELL and PA.ARTICUL=articul1  and PA.EXPIRY_DATE<data_spisania  and CE.BLOCKED_FOR_REMAINS<>1 and CE.OTBOR<>1 order by PA.EXPIRY_DATE 
                            ) where rownum<=1  ; 
                            DBMS_OUTPUT.put_line( 'Флаг4' );
                            dummy2:=to_char( data_spisania, 'DD-MM-YYYY'  );
                            dummy1:= concat(concat(to_char( alternative_date, 'DD-MM-YYYY' ) , ' # ') , dummy2 ) ;
                            
                          --  rret :=concat( concat( concat( concat( Concat('SMOTRI SROK:' ,   alternative_cell) , ' ' ) , alternative_puid ) , ' srok=') , to_char( alternative_date, 'DD-MM-YYYY' ) ); 
                            rret := concat(concat( concat(Concat('SMOTRI SROK:' ,   alternative_cell) , ' [') , dummy1 ) ,  ']' )  ; 
                           dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  rret ,  pallet_id ,  count1  ) ;
                           DBMS_OUTPUT.put_line( 'Флаг5' );
                         return rret;
                      
                      exception
                            WHEN NO_DATA_FOUND THEN  null;
                            WHEN OTHERS THEN  null; 
                        end;
                    end if;
                end if;
             
        exception
                 WHEN NO_DATA_FOUND THEN
                     return 'no_articul';
                 WHEN OTHERS THEN
                  null;
        end;

    end if;

    checks_passed:=1;
end if;

        
    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 
    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event
    -- type_event = 2 , UID_POLETA , USER_ID

    if( checks_passed=0 ) then
     return 'fault';
    end if;
    

  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
 TYPE_EVENT , UID_POLETA , USER_ID ) values
( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );

-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ

commit;

cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);


   RETURN CONCAT('ok_' ,  cell_next );
      
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
          dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '', concat( 'RRL_INTERNAL_MOVE3:err1 ' , cell_to ) ,  pallet_id ,  count1  ) ;
                 
       return 'err1';
     WHEN OTHERS THEN
     dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'RRL_INTERNAL_MOVE3:err2' ,  pallet_id ,  count1  ) ;
       return 'err2';
END RRL_INTERNAL_MOVE3;
/


DROP FUNCTION RABAEV.RRL_TT_REORDER_ADR;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_REORDER_ADR( IDTT int )
 RETURN number IS 
 tmpVar number ;
 data_otgruzki date ; 
 tt int;
-- переделать порядок для паллет , Устоновить плановое время отгрузки для маршрута.

cursor dddd is
SELECT ID , PALLET_UID  , ADDR  , ROWnum as ORD1   FROM (
select  P.ID , P.PALLET_UID  , P.ADDR  , ADR.ORD   from RABAEV.RRL_SBORKA_PALLETS  P  , RRL_ADDR ADR
     where  TRANSTASK_ID  = IDTT  and P.ADDR=ADR.ADDR(+) order by ADR.ORD ,  P.PALLET_UID  ) ;


BEGIN

   tmpVar := 0;
  
for sss in dddd loop
    update RRL_SBORKA_PALLETS set  RRL_SBORKA_PALLETS.ORD= sss.ORD1 where RRL_SBORKA_PALLETS.ID = sss.ID;
end loop;

    tmpVar :=  RRL_GET_TT_PRICE( IDTT ) ;
    update   RRL_TRANSPORT_TASK TT set PRICE = tmpVar where  TT.ID = IDTT ;
 

    tt:=RRL_TT_PLAN_SHIPPPING_HOUR( IDTT ) ;

   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_TT_REORDER_ADR;
/


DROP FUNCTION RABAEV.RRL_PAL_KOR_COUNT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_PAL_KOR_COUNT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum(  RRL_COUNT_KOR2( ARTICUL , QUANTITY ,  CURRENT_MOD_ID  )     )  into tmpVar
 from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 




   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_KOR_COUNT;
/


DROP FUNCTION RABAEV.RRL_TT_ADD_PALL;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ADD_PALL( 
    TT_ID int ,
    ST_NUMBER1 varchar2  
)
 RETURN varchar2 IS 
tmpVar varchar2(1024);
tmpVar2 varchar2(1024);



BEGIN
tmpVar:='OK';

    if( TT_ID>0)then 
        update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID =  TT_ID  where ST_NUMBER= ST_NUMBER1;
    else
        update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID =  null where ST_NUMBER= ST_NUMBER1;
    end if;


    tmpVar:=RABAEV.RRL_TT_REGIONS( TT_ID  );
    update RABAEV.RRL_TRANSPORT_TASK set TEMP_REGION = tmpVar where ID = TT_ID ;
    
    
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 'err2';
       RAISE;
END RRL_TT_ADD_PALL;
/


DROP FUNCTION RABAEV.RRL_TRIAL_BY_WEIGHT2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TRIAL_BY_WEIGHT2( 
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int IS 
    tmpVar number;
    pogr number;
    IDD1 int;
    SPIS_OTBOR_ON_SCAN_OPALL1 int;
    vhelp2 varchar2(255);
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);



--


update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT2(PALLET_UID1)  )<pogr ) then
       
        -- СПИСАНИЕ ОСТАТКОВ 
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    user_id1 );
         end if;
        -- СПИСАНИЕ ОСТАТКОВ 
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = 'ПроверенВесами' where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = 'Выдан в сборку' where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;       
END RRL_TRIAL_BY_WEIGHT2;
/


DROP FUNCTION RABAEV.RRL_UPDATE_PRICE;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_PRICE( tt_id int )
 RETURN number IS 
tmpVar number;
BEGIN
 tmpVar := 0;
   tmpVar := RRL_GET_TT_PRICE(  tt_id ) ;
   
   
   
   update RRL_TRANSPORT_TASK  set price=tmpVar  where ID = tt_id  ;

   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PRICE;
/


DROP FUNCTION RABAEV.RRL_TT_ZONE_FIND_EMPTY_DOCK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_ZONE_FIND_EMPTY_DOCK
(  
  time1      timestamp, 
  ware_id1 int
)

-- Если номер склада пуст
-- По всем докам, доступным к отгрузке,  находим док, 
-- с максимальным расстоянием от предыдущей отгрузки, далее порядком доков.

-- Если номер склада определен, 
-- По всем докам, доступным к отгрузке, с данным номером склада,  находим док, 
-- с максимальным расстоянием от предыдущей отгрузки, далее порядком доков.

RETURN varchar2 IS

ret varchar2(255);

begin 

ret:='';

 if(ware_id1=0  ) then
 
    select DOCK into ret from (
    select DD.DOCK   from RRL_TT_DOCK DD order by RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK( DD.DOCK , time1 ) desc , ord
) where rownum=1;
 
 else
 
        select DOCK into ret from (
        select DD.DOCK   from RRL_TT_DOCK DD where DD.WARE_ID=ware_id1 order by RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK( DD.DOCK , time1 ) desc , ord
        ) where rownum=1;
 
 end if;


   RETURN ret;
exception

    when no_data_found then  RETURN 'NO_DOCK2';
    when others then return 'ERR2';

END  RRL_TT_ZONE_FIND_EMPTY_DOCK;
/


DROP FUNCTION RABAEV.RRL_TT_PLAN_DOCK;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TT_PLAN_DOCK
(  
  TT  int ,
  time1 timestamp ,
  ware_id1 int
)
-- Центральная процедура находящая свободный док , фиксирующая его за маршрутом, 


RETURN int IS    

DOCK1 varchar2(255);


cursor subzones is
    select distinct ZONE from  RABAEV.RRL_TT_ZONES where DOCK=DOCK1 ; 

cursor WW_wares_id is 
    select DISTINCT WARE.PARENT_WARE_ID from RRL_TRANSPORT_TASK TTT , RRL_SBORKA_PALLETS PAL , RRL_WARES WARE where  
     PAL.TRANSTASK_ID = TT and WARE.ID = PAL.WARE_ID order by WARE.ORD2 ; 



    found_dock1 int;         
    found_dock varchar2(255);   
    time2 timestamp ;           
    exit1 int;                  
    count1 int;                 
    ret1 int;                   
    ware_id2 int;
    count_of_pallets int;
    
begin 

/*
    DBMS_OUTPUT.put_line( ' запуск функции  RABAEV.RRL_TT_PLAN_DOCK ' );
    -- ОПРЕДЕЛЯЕМ СКЛАД, ЧЬИ ДОКИ ДОЛЖНЫ ПРЕДЛАГАТЬСЯ 
    ware_id2:=ware_id1;
    if(ware_id1=0) then 
    begin
    select F1 into ware_id2 from (
        select (  WW.PARENT_WARE_ID )  F1  from RRL_TRANSPORT_TASK TT1 , RRL_SBORKA_PALLETS PP , RRL_WARES WW 
            where TT1.ID = TT  and
            PP.TRANSTASK_ID = TT1.ID and PP.WARE_ID=WW.ID order by WW.ORD2 ) where rownum=1 ;
        
        exception
        
            when no_data_found then null; 
            when others then null;
        end;
        
    end if;
    DBMS_OUTPUT.put_line( concat( ' ware_id2 = ' , to_char( ware_id2 ) ) );
--    return 0;
*/

    
for WW_wares_id1  in  WW_wares_id loop -- ЦИКЛ ПО ВСЕМ СКЛАДАМ, ПАЛЛЕТЫ КОТОРЫХУЧАВСТВУЮТ В МАРШРУТЕ 
 
            count1:=0;
            exit1:=0;
            time2:=time1;
            --    Находим док, свободный от погрузки на планируемый момент времени через процедуру RRL_TT_ZONE_FIND_EMPTY_DOCK.
            --    Если док и зона найдена, Фиксируем занятость дока и подзоны путем вызова процедур 
            --    RRL_TT_PLAN_PALL_ZONES - для зон  и маршрутов. Если свободного дока нет, 
            --    увеличиваем время на 30  минут и пробуем снова. 
            --    Если получилось, устанавливаем новое плановое время отгрузки маршрута.


            while  exit1=0 loop
                count1:=count1+1;
                
                found_dock := RRL_TT_ZONE_FIND_EMPTY_DOCK( time2 , WW_wares_id1.PARENT_WARE_ID );
                
                DBMS_OUTPUT.put_line( 'RRL_TT_ZONE_FIND_EMPTY_DOCK = ' ); 
                DBMS_OUTPUT.put_line(found_dock );
                
                if (found_dock = 'NO_DOCK2' or found_dock = ''  ) then 
                    exit1:=0;
                    time2:= time2 + 1/24;
                else
                    exit1:=1;
                end if;
                
                if( count1>10 ) then 
                    exit1:=1;
                    return 0;
                end if;
                
            end loop;


            if( time1<>time2 ) then 
                update RRL_TRANSPORT_TASK set SHIPMENT_TIME=time2 where ID = TT; 
            end if;
            
            -- Теперь для найденного дока находим свободную подзону.
            -- 
        DOCK1 :=found_dock;

        for subzone1 in subzones loop

            count_of_pallets := RRL_TT_ZONE_EMPTY( time1 , subzone1.ZONE ); -- Получаем количество паллет, уже стоящих в зоне. 
            if count_of_pallets=0 then
                ret1:=RRL_TT_PLAN_PALL_ZONES( TT , subzone1.ZONE , time2 , 1 );
                return 1;
                else
                DBMS_OUTPUT.put_line( concat('НЕ НАЙДЕНО ПУСТЫХ ЯЧЕЕК В ЗОНЕ ОТГРУЗКИ НАПРОТИВ ЗОНЫ ' , subzone1.ZONE ) ) ;
            end if;
            
        end loop;

                
         DBMS_OUTPUT.put_line( concat('НЕ НАЙДЕНО ПУСТЫХ ЯЧЕЕК В ЗОНЕ ОТГРУЗКИ НАПРОТИВ ДОКА ' , DOCK1 ) ) ;

end loop; -- ЦИКЛ ПО ВСЕМ СКЛАДАМ, ПАЛЛЕТЫ КОТОРЫХУЧАВСТВУЮТ В МАРШРУТЕ 


    return 0;

exception

    when no_data_found then 
    DBMS_OUTPUT.put_line( 'no_data_found' ) ;
     RETURN 0;
    when others then
    DBMS_OUTPUT.put_line( 'others' ) ;
     return 0;

END   RRL_TT_PLAN_DOCK;
/


DROP FUNCTION RABAEV.RRL_TRIAL_BY_WEIGHT;

CREATE OR REPLACE FUNCTION RABAEV.RRL_TRIAL_BY_WEIGHT( 
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int IS 
    tmpVar number;
    pogr number;
    IDD1 int;
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);



--


update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT(PALLET_UID1)  )<pogr ) then
       
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = 'ПроверенВесами' where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = 'Выдан в сборку' where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;       
END RRL_TRIAL_BY_WEIGHT;
/


DROP FUNCTION RABAEV.RRL_UPDATE_SBORKA_PALLET_ROWS2;

CREATE OR REPLACE FUNCTION RABAEV.RRL_UPDATE_SBORKA_PALLET_ROWS2(

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


