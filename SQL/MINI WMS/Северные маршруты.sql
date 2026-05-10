
/* Formatted on 2010/10/19 18:35  ''(Formatter Plus v4.8.8)  rrl_tt_pallets (t.ID), ROUND (rrl_tt_weight (t.ID), 0),*/


SELECT   t.wave, t.ID,
         t.transtype, t.transport, t.shipment_date, rrl_tt_voditel_info (t.voditel_id),
            rrl_tt_regions (t.ID) , v.DOVERENNOST_OT
    FROM rrl_transport_task t left join RRL_TR_VODITEL v on t.voditel_id = v.ID(+)
    
   WHERE shipment_date >= '01.01.2011'
     AND shipment_date <= '20.10.2011'
     AND t.deleted <> 1
     
     and  ( (rrl_tt_regions (t.ID)  like '%Север;%') or  (rrl_tt_regions (t.ID)  like '%СеверГипермаркет;%')   )

ORDER BY t.ID DESC



