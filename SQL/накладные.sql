
select ddd.* from (

select  ОРГ_УИД_Клиент , Номер , S.УИД , S.Примечание ,   Orders.EXPORTCODE  from 
( 
select  УИД , Примечание  , Номер , r.Накладные.ОРГ_УИД_Клиент  
from r.Накладные where Дата_Закрытия=to_date( '110909' , 'ddmmyy' )
and 

    (   
        SUBSTR( Номер ,1,2)='ЕК' or SUBSTR( Номер ,1,2)='ЗА' or
        SUBSTR( Номер ,2,2)='ЕК' or SUBSTR( Номер ,2,2)='ЗА'
    ) and INSTR (Номер, '/', 1, 1)=0  and INSTR (Номер, 'Z', 1, 1)=0

)  S  left join ROUTEPLANNER.Orders on Orders.EXPORTCODE = S.УИД

)  ddd  where  ( ( ddd.EXPORTCODE ) is null ) 


 

