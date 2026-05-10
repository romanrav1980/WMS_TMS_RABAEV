select 
    h.ADDR ,
    r.ARTICUL ,
    r.QUANTITY ,
    r.ORDER_WEIGHT 
 from 
RABAEV.RRL_SBORKA_PALLET_ROWS  r ,  RABAEV.RRL_SBORKA_PALLETS h
where 

 h.CREATE_DATE > '01.03.2011'
and h.ADDR  like '%Гипер%'

--group by NAKLADDATE




