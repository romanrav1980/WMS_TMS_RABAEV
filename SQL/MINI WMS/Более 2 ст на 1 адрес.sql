
select count (ST_NUMBER) ,  STDATE, ADDR , WARE_ID 

from (

select  distinct ST_NUMBER , STDATE , ADDR , WARE_ID   from 


RRL_SBORKA_PALLETS where  ST_NUMBER  not like '%#%' and ware_id in (4 ,1,2,3)

group by


 STDATE ,  ST_NUMBER  , ADDR , WARE_ID 
 
 )  
 
 group by  STDATE, ADDR , WARE_ID 
 
 having  count (ST_NUMBER)>1
 
 order by STDATE desc