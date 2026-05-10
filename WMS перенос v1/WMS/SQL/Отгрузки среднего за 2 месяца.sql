
 select   art.group_tovara , art.group_tname , 
  
                 sum( rs.order_weight ) вес , 
                 sum( art.last_price*rs.quantity ) СуммаТовара 
                 from rrl_sborka_pallet_rows rs , rrl_sborka_pallets pts , rrl_articuls art , rrl_addr adr where  
                 rs.articul=art.acticul and  pts.addr = adr.addr and  
                 rs.pallet_uid = pts.pallet_uid and pts.transtask_id in (  
                 select   T.ID  from RRL_TRANSPORT_TASK  T   
                 where  deleted<>1  and SHIPMENT_DATE >= '01.03.2012'
                    and SHIPMENT_DATE <=   '01.04.2012'   )  
                 and not ( rs.transport_price is null )  
                 and pts.ware_id in (7,27)
                 
                 group by   
                 art.group_tovara , art.group_tname  , 
                 
                 
                 
                 
