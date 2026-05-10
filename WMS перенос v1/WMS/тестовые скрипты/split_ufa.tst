PL/SQL Developer Test script 3.0
11
begin
  
commit;

  -- Call the function
  :result := pall_splitter.split_ufa(ord_id => :ord_id,
                                     ware_id2 => :ware_id2);
                                    
commit;
                                     
end;
3
result
1
1
4
ord_id
1
28398
4
ware_id2
1
18
4
0
