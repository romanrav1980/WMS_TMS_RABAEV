--  rs.articul , rs.shortname ,
select  sum( rs.original_quantity ) , count(rs.id) , rs.articul , rs.shortname              from
rrl_orders ords , rrl_order_rows rs
where
            rs.order_id=ords.id  
            and ords.create_date>to_date( '19.12.2011' , 'dd.mm.yyyy' )
            and rs.original_quantity<=30
--            and ords.cond in (0,1,2,3,4,5,6,7 )                    
and ords.ware_id=6            
           group by  rs.articul , rs.shortname             
         
         
