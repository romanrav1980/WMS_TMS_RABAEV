select rrl_remains.* from rrl_remains , rrl_articuls , rrl_pallets , rrl_cells where rrl_remains.cell like 'A%' and
     rrl_remains.UID_POLETA = rrl_pallets.UID_PALLET and rrl_pallets.ARTICUL= rrl_articuls.ACTICUL
     and  rrl_articuls.NAME like '%Пиво%' and rrl_cells.CELL = rrl_remains.CELL and rrl_cells.OTBOR=0
   