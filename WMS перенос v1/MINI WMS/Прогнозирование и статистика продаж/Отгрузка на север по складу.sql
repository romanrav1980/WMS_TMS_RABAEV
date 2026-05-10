select 
    r.ARTICUL ,
    art.name ,
    h.ware_id ,
  sum(  r.QUANTITY ) ,
  sum(  r.ORDER_WEIGHT )
 from 
RABAEV.RRL_SBORKA_PALLET_ROWS  r ,  RABAEV.RRL_SBORKA_PALLETS h , rrl_addr adr , rrl_articuls art
where 

r.pallet_uid=h.pallet_uid and
 h.CREATE_DATE > '01.08.2011' and
 h.CREATE_DATE < '01.10.2011' and
 r.articul = art.acticul and
 h.addr = adr.addr AND
 --and  ( adr.region  = 'Север' or  adr.region  = 'СеверГипермаркет' )
 h.ware_id =7
 group by     
           r.ARTICUL ,
           art.name ,
           h.ware_id 

-- Топ товара, отгруженного за сентябрь-ноябрь 2010 г.
--group by NAKLADDATE




