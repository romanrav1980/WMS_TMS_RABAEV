select
ARTICUL , sum(COUNT1) cont
 from
(
select 
ARTICUL , COUNT1
 from
RABAEV.RRL_PRIHOD_NAKLAD_ROWS r , RABAEV.RRL_PRIHOD_NAKLAD h
where 
h.ID = r.ORDID
and condition=2
union


select ARTICUL , (-1)*COUNT1
from 
RABAEV.RRL_OTHOD_NAKLAD_ROWS r , RABAEV.RRL_OTHOD_NAKLAD h
where h.ID= r.ID_NAKLAD
and condition=2

)

group by ARTICUL