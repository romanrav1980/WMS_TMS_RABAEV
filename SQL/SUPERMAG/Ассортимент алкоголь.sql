

   SELECT DISTINCT  c.shortname , smcardassort.ARTICLE   , tree , sacardassort.*  
    FROM supermag.smcardassort , supermag.sacardassort   , supermag.smcard c  
       where idassort=supermag.sacardassort.ID     and ( ( tree  like '82.5%' ) or ( tree like '1.5.1.5%' ) ) 
       and
       
        smcardassort.article = c.article 