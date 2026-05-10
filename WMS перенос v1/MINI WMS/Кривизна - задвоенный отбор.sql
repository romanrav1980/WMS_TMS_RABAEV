
select 
AA.ACTICUL , AA.CELL
from  rrl_articuls AA  where AA.CELL in (


select

 CC.CELL 
 from  rrl_articuls AA , rrl_cells CC
where 
AA.CELL = CC.CELL and CC.cell not like '%---%'


group by  CC.CELL 
having  count( AA.ACTICUL ) >1

)