

SELECT   p.stdate , count( DISTINCT p.pallet_uid ),
         COUNT (r.quantity) ÑÒĞÎÊÈ, SUM (order_weight) ÂÅÑ
    FROM rabaev.rrl_sborka_pallet_rows r,
         rabaev.rrl_sborka_pallets p,
         rrl_addr
   WHERE r.pallet_uid = p.pallet_uid
     AND (p.addr = rrl_addr.addr(+))
     AND (rrl_skladname_by_id (p.ware_id) IN ('ÑÓÕÎÉ' , 'ÏÈÂÎ' ))
     AND (p.stdate >= '01.07.2011')
     AND (p.stdate <= '18.07.2011')
GROUP BY    stdate
 
