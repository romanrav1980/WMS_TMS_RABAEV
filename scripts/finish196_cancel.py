from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_weight_choice_plan")
t=(f/"000_before_choice.sql").read_text(encoding="utf-8")
t=t.replace("old RRL_PICK_WEIGHT_CHOICE%rowtype;result_json json_object_t:=json_object_t();","old RRL_PICK_WEIGHT_CHOICE%rowtype;result_json json_object_t:=json_object_t();active_tasks number;")
t=t.replace("  if old.STATUS='USED'then raise_application_error(-20886,'WEIGHT_CHOICE_CANCEL_ASSOCIATED_PLAN_FIRST');end if;","""  if old.STATUS='USED'then
   select count(*)into active_tasks from RRL_PICK_TASK where PICK_PLAN_LINE_ID=old.PICK_PLAN_LINE_ID and STATUS not in('CANCELLED','FAILED');
   if active_tasks>0 then raise_application_error(-20886,'WEIGHT_CHOICE_CANCEL_ASSOCIATED_PLAN_FIRST');end if;
  end if;""")
g=(f/"003_guard.sql").read_text(encoding="utf-8")
g=g.replace("or :old.STATUS!='ACCEPTED'or :new.STATUS!='CANCELLED'","or :old.STATUS not in('ACCEPTED','USED')or :new.STATUS!='CANCELLED'")
g=g.replace("or :new.PICK_PLAN_ID is not null or :new.PICK_PLAN_LINE_ID is not null or :new.USED_AT is not null\n   then raise_application_error(-20863,'WEIGHT_CHOICE_VALID_CANCELLATION_REQUIRED')","or nvl(:new.PICK_PLAN_ID,-1)!=nvl(:old.PICK_PLAN_ID,-1) or nvl(:new.PICK_PLAN_LINE_ID,-1)!=nvl(:old.PICK_PLAN_LINE_ID,-1)\n   or (:old.USED_AT is null and :new.USED_AT is not null) or (:old.USED_AT is not null and (:new.USED_AT is null or :new.USED_AT!=:old.USED_AT))\n   then raise_application_error(-20863,'WEIGHT_CHOICE_VALID_CANCELLATION_REQUIRED')")
assert "active_tasks>0" in t and "nvl(:new.PICK_PLAN_ID,-1)"in g
print(json.dumps({str(f/"005_choice.sql"):t,str(f/"003_guard.sql"):g,str(f/"006_finish.sql"):"@@005_choice.sql\n@@003_guard.sql\n"},ensure_ascii=True))
