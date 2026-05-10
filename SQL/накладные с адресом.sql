select  R.Организации.Адрес ,  R.Организации.ML_ADDRESS    
from R.Накладные 
 left join R.Организации on ( r.Накладные.ОРГ_УИД_Клиент = R.Организации.ОРГ_УИД and 
 not ( R.Организации.ML_ADDRESS  is null  ) )
 
 where
 
 
  Дата_Закрытия=to_date( '210809' , 'ddmmyy' )
and 
(
SUBSTR( Номер ,1,2)='ЕК' or SUBSTR( Номер ,1,2)='ЗА' or
SUBSTR( Номер ,2,2)='ЕК' or SUBSTR( Номер ,2,2)='ЗА'
) and INSTR (Номер, '/', 1, 1)=0  and INSTR (Номер, 'Z', 1, 1)=0






