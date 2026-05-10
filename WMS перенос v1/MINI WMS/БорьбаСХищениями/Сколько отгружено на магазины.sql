select
 sum( quantity ) ,
 TO_CHAR( pp.CREATE_DATE , 'dd-mm-yyyy'  ) дата , 
 rr.ARTICUL
from RABAEV.RRL_SBORKA_PALLET_ROWS rr  ,   RABAEV.RRL_SBORKA_PALLETS pp  
 where 
 rr.PALLET_UID = pp.PALLET_UID  and 
 rr.ARTICUL = 'Т0000034789'  
 and pp.CREATE_DATE >= '08.12.2010' 
group by  TO_CHAR( pp.CREATE_DATE , 'dd-mm-yyyy'  ) ,
 rr.ARTICUL
 
