from pathlib import Path
import json
src=Path('scripts/ni033_native_wave_case.py').read_text(encoding='utf-8-sig')
src=src.split('  from app.services.case_pick_service import CasePickService',1)[0]
src=src.replace('ware_id=1','ware_id=6667491').replace('values(:c,1,','values(:c,6667491,').replace('values(:id,1,:c','values(:id,6667491,:c').replace('values(:id,:no,:c,1)','values(:id,:no,:c,6667491)').replace('[1,"admin"]','[6667491,"admin"]')
src=src.replace('  q.execute("select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plans[1]);other_pick=int(q.fetchone()[0])','  q.execute("select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plans[1]);other_pick=int(q.fetchone()[0])')
# Keep existing successful stock/core flow, omit its separate foreign-target negative case.
begin=src.index('  meta("update RRL_PICK_TASK set TARGET_CELL_CODE=:c')
end=src.index('  post("TASK_COMPLETE"',src.index('  meta("update RRL_PICK_TASK set TARGET_CELL_CODE=:c',begin+1))
src=src[:begin]+src[end:]
src+='''  print(json.dumps({"tag":tag,"ware":6667491,"article":article,"lot":lot,"revision":revision,"wave":wave,"source_cell":src,"target_cell":dst,"case_ids":[int(row[0])for row in lines]}),flush=True)
 except BaseException:
  print("Own135 fixture stopped; use same partial original documents, do not recreate stock blindly",flush=True)
  raise
'''
print(json.dumps({"scripts/ni081_workload_native_fixture.py":src},ensure_ascii=True))
