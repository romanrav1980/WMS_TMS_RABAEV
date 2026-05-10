select ddd.* from (
select  ОРГ_УИД_Клиент , Номер , S.УИД , S.Примечание , АДРЕС ,  ИМЯ_КЛИЕНТА , Orders.EXPORTCODE  from 
( 
select  Накладные.УИД , Накладные.Примечание  , Накладные.Номер , r.Накладные.ОРГ_УИД_Клиент  , О.АДРЕС
, О.НАИМЕНОВАНИЕ as ИМЯ_КЛИЕНТА
from r.Накладные ,  r.ОРГАНИЗАЦИИ О
 where Дата_Закрытия=to_date( '120909' , 'ddmmyy' )
and Накладные.ОРГ_УИД_КЛИЕНТ=О.УИД
and 
    (   
        SUBSTR( Номер ,1,2)='ЕК' or SUBSTR( Номер ,1,2)='ЗА' or SUBSTR( Номер ,1,2)='ЭЛ' or
        SUBSTR( Номер ,2,2)='ЕК' or SUBSTR( Номер ,2,2)='ЗА' or SUBSTR( Номер ,2,2)='ЭЛ'
    ) and INSTR (Номер, '/', 1, 1)=0  and INSTR (Номер, 'Z', 1, 1)=0
)  S  left join ROUTEPLANNER.Orders on Orders.EXPORTCODE = S.УИД
)  ddd  where  ( ( ddd.EXPORTCODE ) is null ) 


 

