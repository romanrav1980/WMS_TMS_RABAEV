from pathlib import Path
import json
out={}
p=Path('db/migrations/2026-10-10_ni081_transport_edit/001_api.sql');s=p.read_text(encoding='utf-8-sig')
s=s.replace('v_count number:=0;v_global number;', 'v_count number:=0;v_actual_ware number;v_actual_st varchar2(100);v_global number;')
s=s.replace("""   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,item.WARE_ID);
   select ID into v_id from RRL_SBORKA_PALLETS where ID=item.ID for update;""", """   select ID,WARE_ID,ST_NUMBER into v_id,v_actual_ware,v_actual_st from RRL_SBORKA_PALLETS where ID=item.ID for update;
   if v_actual_st!=item.ST_NUMBER then raise_application_error(-20886,'TRANSPORT_SOURCE_ST_CHANGED_RETRY');end if;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,v_actual_ware);""")
out[str(p)]=s
p=Path('db/migrations/2026-10-10_ni081_transport_plan/003_apply.sql');s=p.read_text(encoding='utf-8-sig')
s=s.replace('v_number varchar2(100);v_current number;v_state number;', 'v_number varchar2(100);v_actual_ware number;v_current number;v_state number;')
needle="""   select TRANSTASK_ID,CONDITION into v_current,v_state from RRL_SBORKA_PALLETS where ID=item.ID for update;
   if nvl(v_current,0)!=0 or v_state=2 then"""
new="""   select TRANSTASK_ID,CONDITION,WARE_ID into v_current,v_state,v_actual_ware from RRL_SBORKA_PALLETS where ID=item.ID for update;
   RRL_TRANSPORT_PLAN_RULES.assert_actor(p_actor,v_actual_ware);
   if nvl(v_current,0)!=0 or v_state=2 then"""
assert needle in s;s=s.replace(needle,new)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
