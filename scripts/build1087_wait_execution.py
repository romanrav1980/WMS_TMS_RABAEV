from pathlib import Path
import json
folder="db/migrations/2026-10-13_ni072_shared_wait_target/"
s=Path(folder+"007_hu_boundary.sql").read_text(encoding="utf-8")
s=s.replace("old_case RRL_CASE_PICK_TASK%rowtype;","old_case RRL_CASE_PICK_TASK%rowtype;v_wait_shared boolean:=false;",1)
needle="   v_slot:=m.get_number('target_slot_id');\n   select count(*) into v_count from RRL_REMAINS"
assert needle in s
s=s.replace(needle,"   if v_ignore_task is not null then v_wait_shared:=RRL_ST_DEFER_HU_WAIT.shared_wait_target(p_request,v_ignore_task,v_target,v_ware);end if;\n"+needle,1)
for reason in("CLOSURE_CHANGED: HU target occupied","CLOSURE_CHANGED: HU target container"):
 old="if v_count>0 and v_slot is null then raise_application_error(-20890,'"+reason+"');end if;"
 assert old in s
 s=s.replace(old,old.replace(" then "," and not v_wait_shared then "),1)
p="wiki/database/nicora_ni072_shared_wait_target_20261013.md"
files={folder+"009_hu_execution.sql":s,folder+"fix1087.sql":"@@009_hu_execution.sql\n@@005_compile.sql\n",folder+"apply.sql":Path(folder+"apply.sql").read_text(encoding="utf-8")+"@@fix1087.sql\n",p:Path(p).read_text(encoding="utf-8")+"\n1087: twoTOP case reached A_DONE then B correctly rolled back at execute second empty-target guard. Execution now independently describes actual registered WAIT task under Root locks before shared-target exemption; general HU_MOVE remains exclusive. RRL_STOCK_HU_SLOT target_json and frozenplacementcomparison retained. Resume original Boperation/body; no new stock.\n"}
files["wiki/index.md"]="- [Execute shared target1087](database/nicora_ni072_shared_wait_target_20261013.md): fresh registered WAIT task proof under Root locks, retained A_DONE/B pending.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
files["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1087: two existing TOP first DONE, second atomically refused occupied-target execute guard; targeted same current WAIT proof at execute, resume exact original operation.\n"
print(json.dumps(files,ensure_ascii=True))
