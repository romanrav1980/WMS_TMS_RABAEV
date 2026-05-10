select 
d.id Номер, 
d.createdat Дата, 
d.locationfrom Из_МХ,
d.locationto В_МХ,
s.article Артикул,
c.shortname Название,
s.quantity Колво,
s.itemprice Цена_с_НДС,
s.totalprice Сумма_с_ДС , 
d.COMMENTARY

from supermag.smdocuments d, supermag.smspec s, supermag.smcard c
where d.doctype in ( 'WO' ,  'WI' )  -- 'WI'  приходная,'WO' -- расходная, 'IW' -- на перемещение, если надо
and d.docstate in ( 2 , 3 ) -- статусы 0 - замок, 1 - черновик, 2 - красная,3 - зеленая, если надо
and d.createdat between
to_date('30.01.2010','dd.mm.yyyy') and to_date('30.01.2010','dd.mm.yyyy') -- диапазон дат, если надо
--and d.id = 'ПНХЛТ039368' -- номер накладной, если надо
--and s.article = 'Т0000012233' -- артикул , если надо
and d.id = s.docid and d.doctype = s.doctype 
and s.article = c.article
and  ( d.locationto=2  or d.locationfrom = 2 )


