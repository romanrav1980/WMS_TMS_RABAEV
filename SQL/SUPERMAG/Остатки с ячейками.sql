

SELECT DISTINCT a.article АРТИКУЛ, a.shortname Наименование,
 b.section секция,
 b.pass ряд, 
 b.rack стеллаж, 
 b.stage ярус, 
 b.shelf место,
 
                NVL (dost, 0) остаток
           FROM supermag.smcard a,
                supermag.vcardstoreprop_rc b,
                (SELECT article,
                        (  quantity
                         - reservedquantity
                         - incomingquantity
                         + foundquantity
                        ) dost
                   FROM supermag.smgoods
                  WHERE storeloc = 2) g
          WHERE  
         a.ARTICLE ='Т0000017457' and
          
           a.article = b.article
            AND a.accepted = 1
            AND a.article IN (SELECT article
                                FROM supermag.smcardassort
                               WHERE idassort IN (SELECT ID
                                                    FROM supermag.sacardassort
                                                   WHERE tree LIKE :gr))
            AND a.article = g.article(+)
       ORDER BY b.section,
                TO_NUMBER (b.pass),
                TO_NUMBER (b.rack),
                TO_NUMBER (b.stage),
                TO_NUMBER (b.shelf)