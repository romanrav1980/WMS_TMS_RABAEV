  select 
  cli.ADDRESS , cli.NAME  ,
 c.name , 
  sum( s.quantity  * s.itemprice )  summm 
 
 
 from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli  
 where d.doctype in ( 'WI' , 'OR' )   
  and d.docstate in (     3 )  
 
  and d.id = s.docid and d.doctype = s.doctype  
 and s.article = c.article  and cli.ID = d.CLIENTINDEX  
 
 and  d.createdat > '01.07.2011'
 and d.LOCATIONTO=2
 and ( cli.NAME not like '%Инвента%' )
 and ( cli.NAME not like '%Элемент%' )
 group by   cli.ADDRESS , cli.NAME,
 
  c.name   