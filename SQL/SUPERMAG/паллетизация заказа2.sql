select     article, shortname, replace(bc,';',';'||CHR(10)) bc, abbrev,
         tareweight, path, order_weight, taresize, quantity,
         sum (dd) ddd, dd1 as паллет ,  sortfield, auction
    from (select   *
              from supermag.mon_slkdem_temp t
          order by t.sortfield)
group by section,
         pass,
         pp,
         specitem,
         article,
         shortname,
         bc,
         abbrev,
         tareweight,
         ap,
         aq,
         path,
         order_weight,
         taresize,
         quantity,
         dd1,
         dd2,
         sortfield,
         pr,
         auction
order by sortfield