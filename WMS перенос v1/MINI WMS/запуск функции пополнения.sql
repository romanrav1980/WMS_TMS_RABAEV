

DECLARE
BAKA varchar2(50);
BEGIN
BAKA := RRL_GIVE_POPOLNENIE2  (   'A-4-3-1-3' , 1 );

DBMS_OUTPUT.put_line(  BAKA );

END;


-- select cell  from  RABAEV.RRL_REMAINS  where UID_POLETA='P_T1_3_2' group by cell ;
     

