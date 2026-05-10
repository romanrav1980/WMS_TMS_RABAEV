PL/SQL Developer Test script 3.0
16
-- Created on 13.08.2011 by RRABAEV 
declare 
  -- Local variables here
  i integer;
begin
  -- Test statements here
  
 i:= REVIZION.RRL_INV_CREATE_LINE5(cell1 => 'O-1-1-1-1' ,articul2 => 'Ò0000011955' , count1 =>  600 ,
  expiury_date => to_date('13.08.2011') , fasovka_id1=>1250 , brak_perc1=>3,
pall_weight1=>620 , pall_n => 28, tn_weight1=> 18, count_kor1=>50 , user_id2 => 'R' ,NAKLAD_ID => 45739 );
 
 
 
  
  
end;
0
0
