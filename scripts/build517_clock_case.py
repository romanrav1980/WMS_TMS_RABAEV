import json
from pathlib import Path
v=Path("scripts/ni041_hu_tree_case.py").read_text(encoding="utf-8")
needle='  link("HU_ATTACH",top,box)'
assert v.count(needle)==1
v=v.replace(needle,'''  clock=tree(box)["nodes"][0]["packing_start"]
  assert clock["operation_id"]==op and clock["warehouse"]==1 and clock["instant"][-6]in("+","-"),clock
  assert post("HU_ATTACH",body,{"uid":box},op)==first
  assert tree(box)["nodes"][0]["packing_start"]==clock
  link("HU_DETACH",box,lot,"CLOCK517.DETACH:"+tag)
  # An empty shell retains history; the next actual packing starts a new cycle.
  assert tree(box)["nodes"][0]["packing_start"]==clock
  link("HU_ATTACH",box,lot,"CLOCK517.REPACK:"+tag)
  clock2=tree(box)["nodes"][0]["packing_start"]
  assert clock2["operation_id"]=="CLOCK517.REPACK:"+tag and clock2["content_version"]>clock["content_version"],clock2
  q.execute("select count(*)from RRL_HU_PACK_CYCLE where PARENT_UID=:box",box=box);assert q.fetchone()[0]==2
  try:q.execute("update RRL_HU_PACK_CYCLE set ACTOR='admin'where PARENT_UID=:box",box=box);raise AssertionError("Clock history mutable")
  except oracledb.DatabaseError as exc:conn.rollback();assert exc.args[0].code==20863
  Path("tmp/context517.json").write_text(json.dumps({"tag":tag,"box":box,"first":clock,"second":clock2}),encoding="utf-8")
  print("PASS517 empty creation no clock; first actual scanned packing clock/replay; empty and repack new immutable cycle/aware instant; same P5H2",flush=True)
  link("HU_ATTACH",top,box)''')
v=v.replace('   q.execute("select count(*) from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,)', '   q.execute("select count(*) from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,)\n   assert "packing_start"not in tree(uid)["nodes"][0]')
print(json.dumps({"scripts/case517_box_clock.py":v}))
