from pathlib import Path
import json,hashlib
root="db/migrations/2026-10-14_ni052_departure_temperature/";p=Path(root+"001_thermal_phase.sql")
s=p.read_text(encoding="utf-8")
s=s.replace("member_values json_array_t:=json_array_t.parse(p_members);","member_values json_array_t:=json_array_t.parse(p_members);\n  query_value varchar2(32767);cursor_no integer;query_result integer;rows_cursor sys_refcursor;\n  item_ware number;item_article varchar2(32767);item_lo number;item_hi number;member_no number;")
start=s.index("  for item in(\n");end=s.index("   row_count:=row_count+1;",start)
insert="""  query_value:='select /* CURRENT_LOAD_THERMAL_IN1173 */ distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX from RRL_SBORKA_PALLETS p join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=p.WARE_ID and cfg.ARTICUL=r.ARTICUL where p.ID in (';
  for i in 0..member_values.get_size-1 loop
   if i>0 then query_value:=query_value||',';end if;query_value:=query_value||':id'||to_char(i,'FM999');
  end loop;
  query_value:=query_value||') order by p.WARE_ID,r.ARTICUL fetch first 1001 rows only';
  cursor_no:=dbms_sql.open_cursor;dbms_sql.parse(cursor_no,query_value,dbms_sql.native);
  for i in 0..member_values.get_size-1 loop
   member_no:=member_values.get_number(i);
   if member_no is null or member_no<1 or member_no!=trunc(member_no)then raise_application_error(-20881,'LOAD_THERMAL_MEMBER_ID_REQUIRED');end if;
   dbms_sql.bind_variable(cursor_no,':id'||to_char(i,'FM999'),member_no);
  end loop;
  query_result:=dbms_sql.execute(cursor_no);rows_cursor:=dbms_sql.to_refcursor(cursor_no);cursor_no:=null;
  loop
   fetch rows_cursor into item_ware,item_article,item_lo,item_hi;exit when rows_cursor%notfound;
"""
s=s[:start]+insert+s[end:]
for old,new in(("item.ARTICUL","item_article"),("item.WARE_ID","item_ware"),("item.TEMP_MIN","item_lo"),("item.TEMP_MAX","item_hi")):s=s.replace(old,new)
s=s.replace("  end loop;\n  if row_count=0","  end loop;close rows_cursor;\n  if row_count=0",1)
point=" end;\n procedure assert_current"
handler=""" exception when others then
  if cursor_no is not null then if dbms_sql.is_open(cursor_no)then dbms_sql.close_cursor(cursor_no);end if;end if;
  if rows_cursor%isopen then close rows_cursor;end if;raise;
 end;
 procedure assert_current"""
assert point in s;s=s.replace(point,handler,1)
f={root+"005_thermal_bounded_query.sql":s,root+"apply_bounded_query.sql":"@@005_thermal_bounded_query.sql\n@@004_compile_dependents.sql\n"}
# Preserve installed original1171 source; follow-up separate body source and apply.
f[root+"bounded_checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1173-thermal-bounded-query","target":"RABAEV/orcl","source":"001_thermal_phase.sql","prepared_sha256":hashlib.sha256(s.encode()).hexdigest(),"reason":"Actual1172 JSON_TABLE/hint query675.298ms/13575buffers; replace with bounded200 positional IN binds, at most200 SQL shapes, no literal ID SQL/cursor proliferation/index."},indent=2)
print(json.dumps(f))
