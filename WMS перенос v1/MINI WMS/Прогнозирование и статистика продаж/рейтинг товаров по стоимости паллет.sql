select 
pal.ARTICUL , 
art.name ,
max( pal.UNIT_COUNT  ), 
max( pal.PRICE ),
max( pal.UNIT_COUNT*pal.PRICE ),
max( REMAIN ) , 
RRL_SKLADNAME_BY_ID( cel.ware_id  )

from 

rrl_remains rm , rrl_cells cel , rrl_pallets pal , rrl_articuls art

where rm.cell=cel.cell 
and art.acticul = pal.ARTICUL 
and cel.otbor=0 and BLOCKED_FOR_REMAINS =0
and pal.UID_PALLET= rm.UID_POLETA 
and  pal.PRICE>1
and pal.UNIT_COUNT=REMAIN 


group by pal.ARTICUL , 
art.name ,
RRL_SKLADNAME_BY_ID( cel.ware_id  )