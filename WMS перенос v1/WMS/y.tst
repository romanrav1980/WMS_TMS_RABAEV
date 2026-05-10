PL/SQL Developer Test script 3.0
13
-- Created on 03.06.2011 by RRABAEV 
declare 
  -- Local variables here
  i integer;
begin
  -- Test statements here
  
i :=  GOODS_TO_PICK.create_wtasks(5);

DBMS_OUTPUT.put_line(  i );


end;
0
3
sss
ostat
articul3
