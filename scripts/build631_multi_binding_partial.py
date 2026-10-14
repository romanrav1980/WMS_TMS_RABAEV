from pathlib import Path
import json
source=Path("tmp/630_wave_body.sql").read_text(encoding="utf-8")
a="if v_taken<=0 or old_a.get_size!=1 or p_mode!='FULL_PALLET' then p_decision.put('reason','PARTIAL_TARGET_WHOLE_SINGLE_SOURCE_REQUIRED');return;end if;"
b="""if v_taken<=0 or p_mode!='FULL_PALLET' then p_decision.put('reason','PARTIAL_TARGET_WHOLE_SOURCE_REQUIRED');return;end if;
   -- Release every earlier binding and part of the last one. Multiple remaining
   -- physical sources require a separate plan and are deliberately left untouched.
   x:=treat(old_a.get(old_a.get_size-1)as json_object_t);
   if RRL_STOCK_MATH.quantity(x.get_string('quantity'))<=v_left then
    p_decision.put('reason','PARTIAL_TARGET_MUST_LEAVE_ONE_REDUCED_SOURCE');return;
   end if;"""
assert a in source;value=source.replace(a,b)
a="x:=treat(old_a.get(0) as json_object_t);v_source_uid:=x.get_string('uid');v_source_cell:=x.get_string('cell');"
b="x:=treat(old_a.get(old_a.get_size-1) as json_object_t);v_source_uid:=x.get_string('uid');v_source_cell:=x.get_string('cell');"
assert a in value;value=value.replace(a,b)
a="v_source.put('stock_version',v_source_ver+nvl(p_changes.get_number(v_key),0)+1);"
b="""v_count:=0;
   for i in 0..old_a.get_size-1 loop
    x:=treat(old_a.get(i)as json_object_t);
    if x.get_string('uid')=v_source_uid and x.get_string('cell')=v_source_cell then v_count:=v_count+1;end if;
   end loop;
   v_source.put('stock_version',v_source_ver+nvl(p_changes.get_number(v_key),0)+v_count);"""
assert a in value;value=value.replace(a,b)
d="db/migrations/2026-10-12_ni032_multi_binding_partial/"
out={d+"000_before_wave.sql":source,d+"001_wave.sql":value,d+"apply.sql":"@@001_wave.sql\n",d+"rollback.sql":"@@000_before_wave.sql\n",d+"verify.sql":"select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_WAVE_CMD';\nselect LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_WAVE_CMD';\n"}
print(json.dumps(out,ensure_ascii=True))
