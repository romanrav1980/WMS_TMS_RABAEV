create or replace FUNCTION        RRL_TT_ADD_PALL( 
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
