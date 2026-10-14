from pathlib import Path
import json
old=Path("scripts/case955_case_wait.py").read_text(encoding="utf-8")
head=old[:old.index('context_path=Path("tmp/context955.json")')]
head=head[:head.index('qc_actor="admin"')]+"""qc_actor="admin";cfg=get_settings()
context_path=Path("tmp/context955.json");context=json.loads(context_path.read_text(encoding="utf-8"))
assert context["stage"]=="NEW","Use a separate phase continuation for a progressed source"
tag=context["tag"];lot=context["lot"];ware=context["ware"];article=context["article"];src=context["src"];dst=context["dst"]
def save_context():context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
"""
functions=old[old.index("with oracledb.connect("):old.index(' q.execute("select user,sys_context')]
setup=""" q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code",code=lot);wave=int(q.fetchone()[0])
 q.execute("select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=:w",w=wave);plans=[int(r[0])for r in q.fetchall()]
 q.execute("select CUSTOMER_ORDER_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=:w order by CUSTOMER_ORDER_ID",w=wave);orders=[int(r[0])for r in q.fetchall()]
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 context.update(wave=wave,orders=orders,revision=revision);save_context()
 from app.services.case_pick_service import CasePickService
 CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")
 try:
"""
tail=old[old.index('  released=post("WAVE_PICK_RELEASE"'):old.index('\n finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")',old.index('  print("PASS955'))]
tail=tail.replace('  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])\n  try:q.callproc("RRL_RECEIPT_SETTINGS_API.set_waiting_cell",[ware,wait,"admin"]);conn.commit()\n  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")',
'  meta("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:c where WARE_ID=:ware",c=wait)')
# Existing original typed configuration trigger validates the update; no invented setting API.
source=Path("scripts/ni052_single_case_case.py").read_text(encoding="utf-8")
cleanup=source[source.index("\n finally:\n")+1:]
cleanup=cleanup.replace(' finally:\n',' finally:\n  if "task"in context:\n   meta("update RRL_WAREHOUSE_TASK set STATUS=\'CANCELLED\'where TASK_ID=:id and STATUS not in(\'DONE\',\'CANCELLED\')",id=context["task"])\n',1)
# Keep failed sources for phase continuation. Successful own fixture cleanup only.
cleanup=cleanup.replace(" finally:\n","\n except BaseException as exc:\n  context['error']=str(exc);save_context();raise\n else:\n",1)
cleanup+="\n  context['cleanup']='OWN_P_H_ZERO';save_context()\n"
print(json.dumps({"scripts/resume956_case_wait.py":head+functions+setup+tail+cleanup},ensure_ascii=True))
