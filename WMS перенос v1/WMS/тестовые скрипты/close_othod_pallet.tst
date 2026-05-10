PL/SQL Developer Test script 3.0
18

declare 
cursor sss is
select rs.*  from rrl_sborka_pallet_rows rs, rrl_sborka_pallets pts
where rs.pallet_uid=pts.pallet_uid and pts.condition=2 and rs.id_event is null
and pts.create_date >=  TO_DATE( '17.10.2011 13:19:57' , 'dd.mm.YYYY HH24:MI:SS' )  
and rs.quantity>0

begin
  -- Call the function
  for i in sss loop
 -- update rrl_sborka_pallets pts set pts.condition = 2 where pts.pallet_uid=:pallet_id1
  
  :result := remains_test.close_othod_pallet(pallet_id1 => i.PALLET_UID,
                                             iser_id21 => 'R');
                                             
  end loop;                                           
end;
3
result
1
ok
5
pallet_id1
1
OP_СТвос018152_1
5
iser_id21
1
R
5
0
