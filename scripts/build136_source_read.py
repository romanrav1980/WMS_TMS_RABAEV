from pathlib import Path
import json
p=Path('db/migrations/2026-10-10_ni081_transport_plan/003_apply.sql');s=p.read_text(encoding='utf-8-sig')
old="""  for item in(select ID,ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_tt or ST_NUMBER in
   (select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))order by ID fetch first 201 rows only)loop"""
new="""  for item in(select ID,ST_NUMBER from(
   select ID,ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_tt
   union
   select p.ID,p.ST_NUMBER from RRL_SBORKA_PALLETS p join
    json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$'))j on j.ST_NUMBER=p.ST_NUMBER)
   order by ID fetch first 201 rows only)loop"""
assert old in s;s=s.replace(old,new)
s=s.replace("  v_result.put('stock_changed',false);", "  v_result.put('validation_scope','DECLARED_CAPACITY_TYPE_HYDRO');v_result.put('physical_load_admission',false);\n  v_result.put('stock_changed',false);")
print(json.dumps({str(p):s},ensure_ascii=True))
