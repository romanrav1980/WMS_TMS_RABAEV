select 
d.id Номер, 
s.article Артикул,
s.quantity Колво,
d.createdat Дата, 
c.shortname Название,

d.locationto ,

s.itemprice Цена_с_НДС,
s.totalprice Сумма_с_ДС , 
d.locationfrom Из_МХ,
d.locationto В_МХ,
d.COMMENTARY , 
cli.ADDRESS , 
cli.INN , 
cli.SHORTNAME

from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli
where d.doctype in ( 'WO' ,  'WI' ) 
and d.docstate in ( 2 , 3 ) 
--and d.createdat between to_date('01.02.2012','dd.mm.yyyy') and to_date('28.02.2012','dd.mm.yyyy') 


/* and s.article in (
    SELECT DISTINCT ARTICLE
    FROM supermag.smcardassort , supermag.sacardassort
    where idassort=supermag.sacardassort.ID
    and tree like '1.5.1.5%'
)  */ 


and d.id = s.docid and d.doctype = s.doctype 
and s.article = c.article
and  ( d.locationto<>2  )
and cli.ID = d.CLIENTINDEX
and d.
-- and cli.ADDRESS like '%Уфа%'
-- and inn = '0276085717'
and d.id ='ПНУРС053617'
and ( cli.ID in 
                    (
                        select ss.id from supermag.smstorelocations ss where 
                         ( ss.parentloc  =62 )  or ( name like '%Уфа%' )
                    )

)