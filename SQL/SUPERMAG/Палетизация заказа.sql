        select QuantStDemands.id                                           as "Номер СТ"
             , QuantStDemands.shortname                                    as "Наименование"
             , nvl(QuantStDemands.barcode, 'Нет Ш.К.')                     as "Штрихкод"
             , nvl(QuantStDemands.quantity,0)                              as "Кол-во шт. тов. позиции"
             , QuantStDemands.meaName                                      as "Единица изм."
             , nvl(QuantStDemands.quantYp, 0)                                      as "Кол-во упаковок в месте"
             , nvl(ROUND((QuantStDemands.quantity / QuantStDemands.quantYp),2),0) as "Кол-во упаковок"
             , nvl(ROUND(QuantStDemands.quantity / 
                    (prop_CountPlacesInRow.Kmr * prop_CountRowsInPallet.Krp * QuantStDemands.quantYp),2),0) 
                                                                           as "Кол-во паллет"
          from        
             (
             select sp.article
                  , sp.quantity
                  , car.shortname 
                  , doc.id
                  , (select un2.quantity
                                        from supermag.smStoreUnits un2 
                                       where un2.quantity not in (0,1)
                                         and un2.article = sp.article
                                         and un2.flags   = 0
                                         and rownum = ( select min(rownum)
                                                          from supermag.smStoreUnits un2 
                                                         where un2.quantity not in (0,1)
                                                           and un2.article = sp.article
                                                           and un2.flags   = 0
                                                      )     --в случае, если имеется две записи, 
                                                            --удовлетворяющих критериям отбора, то берется первая из них
                    ) quantYp
                  , (select un2.barcode
                                        from supermag.smStoreUnits un2 
                                       where un2.quantity not in (0,1)
                                         and un2.article = sp.article
                                         and un2.flags   = 0
                                         and rownum = ( select min(rownum)
                                                          from supermag.smStoreUnits un2 
                                                         where un2.quantity not in (0,1)
                                                           and un2.article = sp.article
                                                           and un2.flags   = 0
                                                      )     --в случае, если имеется две записи, 
                                                            --удовлетворяющих критериям отбора, то берется первая из них
                    ) barcode
                  , mea.name  meaName
                  
               from supermag.smstorelocations loc
                  , supermag.smdocuments      doc
                  , supermag.smspec           sp
                  , supermag.smStoreUnits     un
                  , supermag.smcard           car
                  , supermag.sameasurement    mea
              where 
                    doc.doctype               = 'SO'
                and sp.doctype                = 'SO'
                and doc.id                    = sp.docid
                and doc.doctype               = sp.doctype
                --and doc.location              in (P_LOCATID)     
                and loc.id(+)                    = doc.location
                and doc.id  in (  'СТ30л000053'   )                   /*входной параметр номер СТ--'СТ30л000053'*/
                and sp.article                = un.article(+)
                and (un.flags                 =  0 or un.flags is null)
                and sp.article                = car.article
                and car.idmeasurement         = mea.id
                group by  doc.id
                        , sp.article
                        , car.shortname
                        , sp.quantity
                        , mea.name        
             ) QuantStDemands
           , (
             select cp.propval as kmr --кол-во мест в ряду
                  , cp.article
               from supermag.smcardproperties cp
              where cp.propid = '4'
             ) prop_CountPlacesInRow
           , (
             select cp.propval as krp --кол-во рядов в паллете
                  , cp.article
               from supermag.smcardproperties cp
              where cp.propid = '5'
             ) prop_CountRowsInPallet  
       where QuantStDemands.article = prop_CountPlacesInRow.article(+)
         and QuantStDemands.article = prop_CountRowsInPallet.article(+)
      group by   QuantStDemands.id
               , QuantStDemands.shortname
               , QuantStDemands.quantity
               , QuantStDemands.meaName
               , prop_CountPlacesInRow.Kmr
               , prop_CountRowsInPallet.Krp
               , QuantStDemands.quantYp
               , QuantStDemands.barcode
      order by QuantStDemands.id
                ,  QuantStDemands.shortname

         /*select * from supermag.smdocuments t where t.id = 'СТалг000591'
         select * from supermag.smspec y where  y.docid = 'СТалг000591' and y.doctype = 'SO'*/
         
         --select ceil(8 / 3), power(12,2), ROUND(2.047,2) from dual 
      --supermag.SAMeasurement 