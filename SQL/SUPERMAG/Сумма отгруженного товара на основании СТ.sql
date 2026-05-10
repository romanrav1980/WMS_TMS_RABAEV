select 
s.article Артикул,
c.shortname Название,
sum(s.quantity) Колво
from supermag.smdocuments d, supermag.smspec s, supermag.smcard c
where d.doctype in ( 'WO' ,  'WI' , 'IW'  )  -- 'WI'  приходная,'WO' -- расходная, 'IW' -- на перемещение, если надо
and d.docstate in ( 2 , 3 ) -- статусы 0 - замок, 1 - черновик, 2 - красная,3 - зеленая, если надо
and d.id = s.docid and d.doctype = s.doctype 
and s.article = c.article
and d.id in ( select id from  supermag.smcommonbases  where  BASEID='СТаму015039'  and basedoctype='SO' )
group by  s.article , c.shortname 