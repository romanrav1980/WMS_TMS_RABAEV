from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni081_time_source_contract/001_api.sql");s=p.read_text(encoding="utf-8")
needle="  b.put('members',a);a:=json_array_t();n:=0;"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
  for line in(select r.ID,r.PALLET_UID,r.ARTICUL,r.QUANTITY,r.EI,r.ORDER_WEIGHT,r.TAREWEIGHT,r.TARESIZE,r.PACK_COUNT,r.DOCID,r.WARE_ID
   from RRL_SBORKA_PALLET_ROWS r where exists(select 1 from RRL_SBORKA_PALLETS member where member.TRANSTASK_ID=p_trip and member.PALLET_UID=r.PALLET_UID)
   order by r.ID fetch first 2001 rows only)loop
   n:=n+1;if n>2000 then raise_application_error(-20886,'TT_TIME_SOURCE_LINE_BOUND_2000');end if;
   o:=json_object_t();o.put('id',line.ID);o.put('pallet_identifier',line.PALLET_UID);o.put('article',line.ARTICUL);
   o.put('quantity',line.QUANTITY);o.put('unit',line.EI);o.put('order_weight',line.ORDER_WEIGHT);o.put('tare_weight',line.TAREWEIGHT);
   o.put('tare_size',line.TARESIZE);o.put('pack_count',line.PACK_COUNT);o.put('document_id',line.DOCID);o.put('warehouse_id',line.WARE_ID);a.append(o);
  end loop;
  b.put('source_lines',a);a:=json_array_t();n:=0;""")
print(json.dumps({str(p):s},ensure_ascii=True))
