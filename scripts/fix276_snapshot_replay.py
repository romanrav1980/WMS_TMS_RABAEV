from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni072_st_defer/002_api.sql");s=p.read_text(encoding="utf-8")
pos=s.index(" procedure snapshot(")
s=s[:pos]+""" procedure access_st(p_st varchar2,p_actor varchar2,p_right varchar2,p_ware out number)is n number;begin
  select count(distinct WARE_ID),min(WARE_ID)into n,p_ware from RRL_SBORKA_PALLETS where ST_NUMBER=p_st;
  if n!=1 then raise_application_error(-20886,'ST_DEFER_ONE_CURRENT_WARE_REQUIRED');end if;
  scope(p_ware,p_actor,p_right);
 end;
"""+s[pos:]
s=s.replace("a json_array_t:=json_array_t();b json_object_t:=json_object_t();item json_object_t;v_count number:=0;","a json_array_t:=json_array_t();cargo json_array_t:=json_array_t();b json_object_t:=json_object_t();item json_object_t;v_count number:=0;v_cargo number:=0;",1)
needle="  b.put('st_number',p_st);"
pos=s.index(needle)
cargo="""  for x in(select r.ID,r.PALLET_UID,r.ARTICUL,r.EI,r.QUANTITY,r.PACK_COUNT,r.ORDER_WEIGHT,r.TAREWEIGHT,r.TARESIZE
   from RRL_SBORKA_PALLET_ROWS r join RRL_SBORKA_PALLETS p on p.PALLET_UID=r.PALLET_UID where p.ST_NUMBER=p_st
   order by r.PALLET_UID,r.ID fetch first 10001 rows only)loop
   v_cargo:=v_cargo+1;if v_cargo>10000 then raise_application_error(-20886,'ST_DEFER_CARGO_BOUND_10000');end if;
   item:=json_object_t();item.put('id',x.ID);item.put('pallet_identifier',x.PALLET_UID);item.put('articul',x.ARTICUL);item.put('unit_code',x.EI);
   item.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.QUANTITY));item.put('pack_count',RRL_STOCK_PLAN_HELPER.decimal_text(x.PACK_COUNT));
   item.put('weight',RRL_STOCK_PLAN_HELPER.decimal_text(x.ORDER_WEIGHT));item.put('pack_weight',RRL_STOCK_PLAN_HELPER.decimal_text(x.TAREWEIGHT));item.put('pack_size',RRL_STOCK_PLAN_HELPER.decimal_text(x.TARESIZE));
   cargo.append(item);
  end loop;
  b.put('cargo',cargo);
"""
s=s[:pos]+cargo+s[pos:]
s=s.replace("  snapshot(v_st,p_actor,'transport_dispatch_edit',src,hash,ware,source_trip);\n  request_hash", "  access_st(v_st,p_actor,'transport_dispatch_edit',ware);\n  request_hash",1)
s=s.replace("  snapshot(v_st,p_actor,'transport_dispatch_edit',src,hash,ware,source_trip);\n  begin select *into saved", "  access_st(v_st,p_actor,'transport_dispatch_edit',ware);\n  begin select *into saved",1)
s=s.replace("  if source_trip=target_trip then","  snapshot(v_st,p_actor,'transport_dispatch_edit',src,hash,ware,source_trip);\n  if source_trip=target_trip then",1)
print(json.dumps({str(p):s},ensure_ascii=True))
