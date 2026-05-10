

DECLARE
BAKA varchar2(50);
BEGIN



 -- BAKA := RRL_REVIZION_CELL_KOR( 'D-1-2-1-2' , 38 , 'R' );  --RRL_PRIHODPALLET_CALC_COUNT( 'P_Ò0000082836_35156_1' ,  933 , 1 );   

BAKA :=  GOODS_TO_PICK.create_wtasks(5);

DBMS_OUTPUT.put_line(  BAKA );



END;
