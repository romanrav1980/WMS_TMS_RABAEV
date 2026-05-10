
select distinct
art.acticul , art.name , pts.mod_id , rrl_get_mod_info( pts.mod_id ) ,
 mds.sht_in_kor , mds.sht_weight , mds.karton_weight 

 from rrl_remains rr , rrl_cells cel , rrl_pallets  pts , rrl_articuls art , 
rrl_articul_mods  mds

where
cel.ware_id=7 and cel.cell = rr.cell 
and pts.uid_pallet=rr.uid_poleta
and art.acticul = pts.articul
and mds.id= pts.mod_id
and cel.blocked_for_remains=0


