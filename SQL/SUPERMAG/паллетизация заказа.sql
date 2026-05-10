select   1 as gi, section, pass, pp, specitem, article, shortname, replace(bc,';',';'||CHR(10)) bc, abbrev,
         tareweight, ap, aq, path, order_weight, taresize, quantity,
         sum (dd) ddd, dd1 as dds1, dd2 as ddr2, sortfield,pr,auction
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