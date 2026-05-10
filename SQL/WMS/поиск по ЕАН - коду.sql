select * from  

 refstock.tb_art  ar left join refstock.tb_ean  ean
on  ar.ar_cproin = ean.ea_cproin
 
where ea_ean13  = '4602162000893'
 
 
 