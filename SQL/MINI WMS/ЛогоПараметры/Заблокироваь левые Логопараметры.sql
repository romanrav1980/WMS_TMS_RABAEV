

select distinct
mds.id ,
art.acticul , art.name ,  
 mds.sht_in_kor , mds.sht_weight , mds.karton_weight 

 from   rrl_cells cel ,   rrl_articuls art , 
rrl_articul_mods  mds

where
cel.ware_id=7 
and cel.cell= art.cell
and mds.articul=art.acticul
and mds.id  not in ( -- Модификации на остатках 
    select distinct pts.mod_id 
     from rrl_remains rr , rrl_cells cel , rrl_pallets  pts , rrl_articuls art , 
    rrl_articul_mods  mds
    where
    cel.ware_id=7 and cel.cell = rr.cell 
    and pts.uid_pallet=rr.uid_poleta
    and art.acticul = pts.articul
    and mds.id= pts.mod_id
    and cel.blocked_for_remains=0
)
and art.acticul not in ( -- Артикулы с  единственной модификацией
    select art.acticul from rrl_articuls art , rrl_articul_mods mds where mds.articul=art.acticul
    having  count( art.acticul )<=1 group by art.acticul
)
