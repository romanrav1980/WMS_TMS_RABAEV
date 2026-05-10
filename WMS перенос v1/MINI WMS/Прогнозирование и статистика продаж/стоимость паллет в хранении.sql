

select
art.name ,  
  cl.ware_id , pts.articul , cl.cell , sum( pts.price* pts.unit_count ) —“Œ»ÃŒ—“‹_“Œ¬¿–¿ , 
  count( DISTINCT pts.uid_pallet  ) ÍÓÎ‚Ó_Ô‡ÎÎ
    
 from 
rrl_remains rm , rrl_cells cl  , rrl_pallets pts , rrl_articuls art
where rm.cell = cl.cell and cl.blocked_for_remains=0 and cl.otbor=0
and rm.uid_poleta=pts.uid_pallet 
and rm.remain>0 
and pts.articul = art.acticul
and art.name like '%œË‚Ó%'

group by  art.name ,  cl.ware_id , pts.articul , cl.cell 
