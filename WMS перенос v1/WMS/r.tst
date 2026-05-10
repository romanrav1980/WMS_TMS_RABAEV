PL/SQL Developer Test script 3.0
11
-- Created on 29.05.2011 by RRABAEV 
declare 
  -- Local variables here
  i integer;
begin
  -- Test statements here
  i:= COMPL.update_seq('dd' , 3 ,4,5);
DBMS_OUTPUT.put_line( to_char(i) );
DBMS_OUTPUT.put_line( 'hello2');
commit;
end;
1
i
0
0
0
