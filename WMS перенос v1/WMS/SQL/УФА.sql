select 
s.article Артикул,
c.name ИмяТовара , 
sum( s.totalprice ) Сумма_с_ДС ,
cli.ADDRESS , 
cli.name , 
cli.INN 
from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli
where d.doctype in ( 'WO' ,  'WI' ) 
and d.docstate in ( 2 , 3 ) 
and d.createdat between to_date('01.02.2012','dd.mm.yyyy') and to_date('28.02.2012','dd.mm.yyyy') 
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
and d.locationto in (
313 , 253 , 369 , 211 , 459 , 
377 , 282 , 219  , 280 , 305 , 412 , 
283 , 215 , 441 ,224 , 350 , 381 , 329 , 
210 , 322 , 406 , 233 , 227 , 231 , 236 , 295 , 235 , 225 , 234 , 216 , 218 , 
223 , 237 , 370 , 343 , 287 )
-- and inn = '0276085717'
--and d.id ='ПНУРС053617'
/* and ( cli.ID in 
                    (
                        select ss.id from supermag.smstorelocations ss where 
                         ( ss.parentloc  =62 )  or ( name like '%Уфа%' )
                    )
)  */   
group by 
s.article  ,
cli.ADDRESS , 
cli.INN , cli.name , c.name 
