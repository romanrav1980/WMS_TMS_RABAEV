

select c.article, c.shortname, sp.propval "РЦЕ Комплект" , sp1.propval "Порядок комплектации"
  from supermag.smcard c, supermag.smcardproperties sp , supermag.smcardproperties sp1
 where c.article = sp.article
   and sp.propid = 'User.RCComplect'
    and sp1.propid = 'User.pcsort'
    and c.article = sp1.article


