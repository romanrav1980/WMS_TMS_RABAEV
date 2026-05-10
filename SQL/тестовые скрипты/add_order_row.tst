PL/SQL Developer Test script 3.0
7
begin
  -- Call the function
  :result := orders.add_order_row(ord_id => :ord_id,
                                  articul1 => :articul1,
                                  quantity1 => :quantity1,
                                  ware_id1 => :ware_id1);
end;
5
result
1
-1
4
ord_id
1
37763
4
articul1
1
Ò0000139697
5
quantity1
1
9
4
ware_id1
1
3
4
0
