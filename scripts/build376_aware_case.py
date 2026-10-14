from pathlib import Path
import json
p=Path("scripts/ni042_marked_small_mass_case.py");t=p.read_text(encoding="utf-8").replace("211","376")
at=t.index('api=httpx.Client')
t=t[:at]+'''if Path("tmp/context376.json").exists()or Path("tmp/progress376.json").exists():raise SystemExit("Own376 already started; resume retained context")
Path("tmp/progress376.json").write_text(json.dumps({"tag":tag,"warehouse":ware,"article":article,"sscc":sscc}),encoding="utf-8")
'''+t[at:]
needle='  print("PASS376 marked small CASE'
at=t.index(needle)
t=t[:at]+'''  q.execute("select to_char(STARTED_AT_INSTANT,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:case_id",case_id=case)
  instant=q.fetchone()[0];assert instant is not None
  Path("tmp/context376.json").write_text(json.dumps({"tag":tag,"warehouse":ware,"article":article,"case":int(case),"trip":int(trip),"load_operation_id":op,"carrier":carrier,"parent":parent,"start_instant":instant,"store":store,"units":units,"case_scans":scans},indent=2),encoding="utf-8")
'''+t[at:]
print(json.dumps({"scripts/source376_aware_small_case.py":t}))
