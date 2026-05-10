select
sum( count_event ) колво , 
TO_CHAR( ee.date_event , 'dd-mm-yyyy'  ) , 
PP.ARTICUL
 from rrl_events EE , rrl_pallets PP , rrl_cells CC 
 where 
EE.UID_POLETA = PP.UID_PALLET and 
PP.ARTICUL = 'Т0000034789' and
ee.date_event >= '01.11.2010'  and
CC.cell = EE.cell_to and 
CC.otbor=1 and 
CC.is_system =0
group by TO_CHAR(ee.date_event , 'dd-mm-yyyy'  ) , PP.ARTICUL
