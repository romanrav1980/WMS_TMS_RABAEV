select 
  sum( count1 ) as sum2 
 from 
RABAEV.RRL_OTHOD_NAKLAD_ROWS  r ,  RABAEV.RRL_OTHOD_NAKLAD h
where  articul = 'Ò0000114939'
and h.ID = r.ID_NAKLAD
and NAKLADDATE > sysdate - 10

--group by NAKLADDATE