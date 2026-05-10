  select 
  cli.ADDRESS , cli.NAME  ,
 
  sum( s.quantity  * s.itemprice )  summm , cc.tree,cc.name
 
 from supermag.smdocuments d, supermag.smspec s, SUPERMAG.SMCLIENTINFO cli  , 
 supermag.smcard c join SUPERMAG.SACARDCLASS cc on cc.id = c.idclass
 where d.doctype in ( 'WI' , 'OR' )   
  and d.docstate in (     3 )  
 
  and d.id = s.docid and d.doctype = s.doctype  
 and s.article = c.article  and cli.ID = d.CLIENTINDEX  
 
 and  d.createdat > '01.11.2011'
 and d.LOCATIONTO=2
 and cli.NAME not like '%Элемент-Трейд%'
 and cli.NAME not like '%Инвентаризация%'
 and cli.NAME not like '%наценка%' 
 and cli.NAME not like '%Дионис%' 
  
 group by   cli.ADDRESS , cli.NAME  , cc.tree,cc.name 
 
 
 
