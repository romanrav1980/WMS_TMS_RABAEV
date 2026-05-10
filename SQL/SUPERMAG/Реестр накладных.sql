select 
d.id Номер, 
d.createdat Дата, 
d.locationfrom Из_МХ,
d.locationto В_МХ,
d.CLIENTINDEX ,
d.COMMENTARY ,
cli.NAME
from supermag.smdocuments d , SUPERMAG.SMCLIENTINFO cli
where d.doctype in ( 'WO' ,  'WI' )  -- 'WI'  приходная,'WO' -- расходная, 'IW' -- на перемещение, если надо
and d.docstate in ( 2 , 3 ) -- статусы 0 - замок, 1 - черновик, 2 - красная,3 - зеленая, если надо
and d.createdat between
to_date('30.01.2010','dd.mm.yyyy') and to_date('30.01.2010','dd.mm.yyyy') -- диапазон дат, если надо
and  ( d.locationto=2  or d.locationfrom = 2 )
and cli.ID = d.CLIENTINDEX