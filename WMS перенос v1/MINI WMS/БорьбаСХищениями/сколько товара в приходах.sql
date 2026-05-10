


select sum(unit_count) ,

 TO_CHAR( pp.CREATION_DATE , 'dd-mm-yyyy'  )

from rrl_pallets pp
where 
pp.ARTICUL= 'Ò0000034789'

group by 
 TO_CHAR( pp.CREATION_DATE , 'dd-mm-yyyy'  )