from pathlib import Path
v=Path("scripts/source385_marked_reuse.py").read_text(encoding="utf-8").replace("385","622")
a='  departed=loading.depart("IW622.DEPART:"+tag,trip,"admin")'
assert a in v
b='''  from app.modules.platform.public import read_oracle_json
  profile=read_oracle_json(q.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[vehicle]))
  profile_body=dict(operation_id="VEH.RETURN622:"+tag,vehicle_id=vehicle,vehicle_size_class="DEV.RETURN622",
     cargo_length_mm=3000,cargo_width_mm=2000,cargo_height_mm=2200,expected_version=0,
     expected_source_hash=profile["base_hash"],reason="Synthetic isolated return source vehicle profile",
     evidence_reference="DEV622:"+tag)
  profile_result=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(profile_body),"admin",profile_result]);conn.commit()
'''+a
v=v.replace(a,b)
# Do not reproduce old success statements for skipped cases.
v=v.replace("SOURCE622 actualSAP3EA","SOURCE622 new isolated actualSAP3EA")
Path("scripts/source622_return_aggregate.py").write_text(v,encoding="utf-8")
v=Path("scripts/deliver386_reuse_source.py").read_text(encoding="utf-8").replace("context385.json","context622.json").replace("386","623")
Path("scripts/deliver623_return_aggregate_source.py").write_text(v,encoding="utf-8")
print("622/623 fresh source derived from existing verified fullBOX fixture; old385/386 never rerun, supplier aggregates reused, vehicle profile before departure.")
