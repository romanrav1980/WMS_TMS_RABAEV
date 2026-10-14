from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni022_late_loaded_assignment");out={}
s=(f/"000_before_rrl_transport_plan_rules.sql").read_text(encoding="utf-8")
s=s.replace("strict_windows number;bad number;","strict_windows number;bad number;actual_places number;actual_weight number;actual_bad number;",1)
s=s.replace("""where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')));
  if places>v.PALLETS""","""where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
    and not exists(select 1 from RRL_TT_HU_LOAD_ST m join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1 and l.STATUS='LOADED');
   select nvl(sum(l.PHYSICAL_PLACES),0),nvl(sum(l.GROSS_WEIGHT_KG),0),
    nvl(sum(case when l.PHYSICAL_PLACES is null or l.PHYSICAL_PLACES<=0 or l.GROSS_WEIGHT_KG is null or l.GROSS_WEIGHT_KG<=0 or o.STATE!='APPLIED' or o.STATE is null then 1 else 0 end),0)
    into actual_places,actual_weight,actual_bad from RRL_TT_HU_LOAD_FACT l
    left join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
    where l.STATUS='LOADED'and l.LOAD_OPERATION_ID in(
     select m.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS p on p.ID=m.SBORKA_PALLET_ID
     where m.ACTIVE_FLAG=1 and p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
    );
   if actual_bad>0 then raise_application_error(-20886,'PLAN_LOADED_PHYSICAL_CAPACITY_PROOF_REQUIRED');end if;
   places:=nvl(places,0)+actual_places;weight:=nvl(weight,0)+actual_weight;unknown_weight:=nvl(unknown_weight,0);
   if weight>v.MAX_WEIGHT_KG then raise_application_error(-20886,'PLAN_WEIGHT_CAPACITY_EXCEEDED');end if;
  if places>v.PALLETS""",1)
assert "PLAN_LOADED_PHYSICAL_CAPACITY_PROOF_REQUIRED"in s
s=s.replace("result.put('declared_places',places);","result.put('frozen_loaded_places',actual_places);result.put('frozen_loaded_weight_kg',to_char(actual_weight,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));result.put('declared_places',places);",1)
out[str(f/"001_rules.sql")]=s
s=(f/"000_before_rrl_transport_plan_api.sql").read_text(encoding="utf-8")
s=s.replace("v_check clob;v_out json_object_t;","v_check clob;v_out json_object_t;v_loaded number;v_preserved number:=0;v_writable json_array_t:=json_array_t();v_requested_state number;v_condition varchar2(100);",1)
s=s.replace("if nvl(v_old,0)not in(0,p_tt)or v_state=2 then raise_application_error(-20886,'PLAN_ST_FOREIGN_OR_SHIPPED');end if;","""if nvl(v_old,0)not in(0,p_tt)then raise_application_error(-20886,'PLAN_ST_FOREIGN_OR_SHIPPED');end if;
    if v_state=2 then
     select count(*)into v_loaded from RRL_TT_HU_LOAD_ST m join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
      where m.SBORKA_PALLET_ID=item.ID and m.ACTIVE_FLAG=1 and l.TT_ID=p_tt and l.VEHICLE_ID=v_vehicle and l.VEHICLE_NUMBER=v_num and l.STATUS='LOADED'and l.CUSTODY_RELEASED_AT is null and o.STATE='APPLIED';
     select CONDITION into v_condition from RRL_TRANSPORT_TASK where ID=p_tt;
     if v_old is null or v_old!=p_tt or v_loaded!=1 or v_condition is null or v_condition!='Спланирован'then raise_application_error(-20886,'PLAN_ST_FOREIGN_OR_SHIPPED');end if;
     v_preserved:=v_preserved+1;
    end if;""",1)
s=s.replace("write_members(p_tt,v_requested);v_out:=json_object_t.parse(v_check);","""for i in 0..v_requested.get_size-1 loop
    select CONDITION into v_requested_state from RRL_SBORKA_PALLETS where ST_NUMBER=v_requested.get_string(i);
    if nvl(v_requested_state,0)!=2 then v_writable.append(v_requested.get_string(i));end if;
   end loop;
   if v_writable.get_size>0 then write_members(p_tt,v_writable);end if;
   v_out:=json_object_t.parse(v_check);v_out.put('retained_loaded_sts',v_preserved);v_out.put('written_sts',v_writable.get_size);""",1)
# SQL cannot reference JSON object method directly.
s=s.replace("v_condition varchar2(100);","v_condition varchar2(100);v_requested_number varchar2(100);",1).replace("select CONDITION into v_requested_state from RRL_SBORKA_PALLETS where ST_NUMBER=v_requested.get_string(i);","v_requested_number:=v_requested.get_string(i);select CONDITION into v_requested_state from RRL_SBORKA_PALLETS where ST_NUMBER=v_requested_number;",1)
out[str(f/"002_assignment.sql")]=s
print(json.dumps(out,ensure_ascii=True))
