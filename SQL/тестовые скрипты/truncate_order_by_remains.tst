PL/SQL Developer Test script 3.0
13
-- Created on 13.08.2011 by RRABAEV 
declare 
  -- Local variables here
  i integer;
begin
  -- Test statements here

  i:=COMPL.orders_start_plan(  252 );
  i:=COMPL.orders_start_plan(  253 );  
  i:=COMPL.truncate_order_by_remains(  16 ) ;
  
  
end;
0
0
