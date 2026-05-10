PL/SQL Developer Test script 3.0
8
begin
  -- Call the function
  :result := compl.sborka_full_pall_pick3(sb_pall_uid_coded => :sb_pall_uid_coded,
                                          hran_pall_uid1 => :hran_pall_uid1,
                                          cell1 => :cell1,
                                          user_id1 => :user_id1,
                                          pall_weight => :pall_weight);
end;
6
result
1
ok
5
sb_pall_uid_coded
1
W6P1257529
5
hran_pall_uid1
1
﻿P_Т0000142059_61265_2
5
cell1
1
O-3-1-3-1
5
user_id1
1
R
5
pall_weight
1
800
5
0
