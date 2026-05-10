select  TB_EINV.* ,

EI_DEBINV  ДатаНачала, 
EI_DEPOT ,
EI_FININV ДатаКонца

from TB_EINV

Where 
EI_DEBINV > to_date( '131209' , 'ddmmyy' ) 
and EI_STATUT=1
and  EI_ZONE='Q'
and EI_DEPOT='01'

