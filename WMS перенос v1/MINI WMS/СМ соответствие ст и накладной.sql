select d.id, d.createdat, b.baseid
  from supermag.smdocuments d, supermag.smcommonbases b
  where d.doctype='WO'
and d.docstate=2
    and b.doctype='WO'
    and b.basedoctype='SO'
    and d.id=b.id
  and b.baseid in (select d1.id 
  from supermag.smdocuments d1 
  where d1.doctype='SO'
    and d1.docstate=2)