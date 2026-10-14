from pathlib import Path
import json
out={}
p=Path('db/migrations/2026-10-10_ni081_transport_plan/003_apply.sql');s=p.read_text(encoding='utf-8-sig')
s=s.replace('v_row_count number:=0;v_check clob;', 'v_row_count number:=0;v_check clob;v_all_text clob;v_vehicle_text clob;v_row_text clob;v_rows json_array_t:=json_array_t();v_found_keys json_key_list;')
s=s.replace('  for item in(select ID from json_table(v_vehicles.to_clob', '  v_all_text:=v_all.to_clob;v_vehicle_text:=v_vehicles.to_clob;\n  for item in(select ID from json_table(v_vehicle_text')
s=s.replace('json_table(v_all.to_clob,', 'json_table(v_all_text,')
s=s.replace('v_row_count:=v_row_count+1;if v_row_count>5000', 'v_row_count:=v_row_count+1;v_rows.append(item.ID);if v_row_count>5000')
s=s.replace('  if v_found.get_keys.count!=v_all.get_size', '  v_found_keys:=v_found.get_keys;\n  if v_found_keys.count!=v_all.get_size')
old="""  for item in(select ID from RRL_SBORKA_PALLETS where ST_NUMBER in
   (select ST_NUMBER from json_table(v_all_text,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))order by ID)loop"""
new="""  v_row_text:=v_rows.to_clob;
  for item in(select ID from json_table(v_row_text,'$[*]'columns(ID number path '$'))order by ID)loop"""
assert old in s;s=s.replace(old,new)
s=s.replace("  v_result.put('plan_id',p_plan);", """  select count(*)into v_current from RRL_SBORKA_PALLETS where ST_NUMBER in
   (select ST_NUMBER from json_table(v_all_text,'$[*]'columns(ST_NUMBER varchar2(100)path '$')));
  if v_current!=v_row_count then raise_application_error(-20886,'PLAN_SOURCE_ROWS_CHANGED_RETRY');end if;
  v_result.put('source_member_ids',v_rows);
  v_result.put('plan_id',p_plan);""")
out[str(p)]=s
p=Path('db/migrations/2026-10-10_ni081_transport_plan/002_rules.sql');s=p.read_text(encoding='utf-8-sig')
s=s.replace("nvl(v.MAX_WEIGHT_KG,0)<=0 then", "nvl(v.MAX_WEIGHT_KG,0)<=0 or v.TR_TYPE is null then")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
