
select 
  cli.NAME   ,  c.article  -- , sum( s.quantity  * s.itemprice )  summm  
 from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli  
 where d.doctype in ( 'WI' , 'OR' )   
  and d.docstate in (     3 )  
 
  and d.id = s.docid and d.doctype = s.doctype  
 and s.article = c.article  and cli.ID = d.CLIENTINDEX  
 and  d.createdat > '01.07.2011'
 and d.LOCATIONTO=2
 and not  cli.NAME like '%Элемент%'  and not  cli.NAME like '%Дионис%' and not  cli.NAME like '%Инвент%'
 group by   cli.NAME  ,  c.article
 
 
 