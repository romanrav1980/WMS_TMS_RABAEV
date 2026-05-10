DECLARE
BAKA varchar2(50);
BEGIN



DBMS_OUTPUT.put_line(  'начало' );
--BAKA:= RABAEV.RRL_GET_ST_IS_SCANNED( 'СТлпо004899' );

BAKA:= RABAEV.RRL_DAY_DISTRIBUTE_ENDS( 'Т0000082836',  to_date( '09.04.2011' , 'dd.mm.yyyy' ) );



DBMS_OUTPUT.put_line(  BAKA );




END;