  select
  d.id ,   
  cli.ADDRESS , cli.NAME ,   cli.ID 
 d.createdat ,  
  s.article  , 
  s.quantity  ,  
  s.itemprice  ,  
 c.shortname  
 
 
 from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli  
 where d.doctype in ( 'WI' , 'OR' )   
  and d.docstate in (     3 )  
 
  and d.id = s.docid and d.doctype = s.doctype  
 and s.article = c.article  and cli.ID = d.CLIENTINDEX  
 
 and  d.createdat > '01.08.2011'
 and d.LOCATIONTO=2
 group by 