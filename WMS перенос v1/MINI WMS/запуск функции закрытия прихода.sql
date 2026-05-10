

DECLARE
BAKA varchar2(50);
BEGIN
BAKA := RRL_ACCEPT_ORDER2_3  (   25845  , 'R' );

DBMS_OUTPUT.put_line(  BAKA );

END;


-- select cell  from  RABAEV.RRL_REMAINS  where UID_POLETA='P_T1_3_2' group by cell ;
     

