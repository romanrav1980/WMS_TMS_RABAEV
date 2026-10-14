from pathlib import Path
import json
src=Path("scripts/case867_same_source.py").read_text(encoding="utf-8").replace("867","879")
src=src.replace("def post(kind,body,source,op=None):","def post(kind,body,source,op=None,actor='admin'):")
src=src.replace('"command_type":kind,"actor":"admin"','"command_type":kind,"actor":actor')
src=src.replace('[inp,"admin",out,None]','[inp,actor,out,None]')
needle='  Path("tmp/context879.json").write_text(json.dumps({"wave":wave,"rt":rt,"task"'
idx=src.index(needle)
addition="""  from app.modules.inventory.infrastructure.wave_pick_release import WavePickRelease
  from fastapi import HTTPException
  readiness=WavePickRelease(gateway).preview(wave,"admin")
  assert readiness["ready"],readiness
  q.execute("select WARE_ID,nvl(DELETED,0)from RUSERS where ID='QA172_KRO'")
  foreign=q.fetchone();assert foreign is not None and foreign[0]!=ware and foreign[1]==0,foreign
  try:WavePickRelease(gateway).preview(wave,"QA172_KRO");raise AssertionError("Foreign warehouse read accepted")
  except HTTPException as exc:assert exc.status_code==403,exc
  try:post("WAVE_PICK_RELEASE",{},{ "wave_id":wave},"PICK879.FOREIGN:"+tag,actor="QA172_KRO");raise AssertionError("Foreign warehouse command accepted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882 and "WAVE_CURRENT_WARE_FORBIDDEN"in str(exc),exc
  release=post("WAVE_PICK_RELEASE",{},{ "wave_id":wave},"PICK879.ALLOW:"+tag)
  assert release["released_at"] and release["release_operation_id"]=="PICK879.ALLOW:"+tag,release
  assert post("WAVE_PICK_RELEASE",{},{ "wave_id":wave},"PICK879.ALLOW:"+tag)==release
  print("PASS879 current admin readiness/release/exact replay; foreign QA172_KRO native command and scoped read refused403/20882",flush=True)
"""
src=src[:idx]+addition+src[idx:]
print(json.dumps({"scripts/case879_pick_scope.py":src},ensure_ascii=True))
