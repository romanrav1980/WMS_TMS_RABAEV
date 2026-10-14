from pathlib import Path
import json
p=Path("db/migrations/2026-10-10_ni081_operation_plan/001_api.sql")
s=p.read_text(encoding="utf-8").replace('v_count number:=0;v_global number;','v_route_drive number;v_route_back number;v_route_basis varchar2(50);\n  v_count number:=0;v_global number;')
s=s.replace('for i in 0..chain.get_size-1 loop\n   v_code', 'RRL_TT_ROUTE_SOURCE.durations(p_trip,p_actor,v_route_drive,v_route_back,v_route_basis);\n  for i in 0..chain.get_size-1 loop\n   v_code')
s=s.replace('if v_per=1 then v_duration:=v_duration*v_places;end if;','if v_per=1 then v_duration:=v_duration*v_places;end if;\n   if v_code=\'DRIVE\'and v_route_drive is not null then v_duration:=v_route_drive;end if;\n   if v_code=\'DRIVE_BACK\'and v_route_back is not null then v_duration:=v_route_back;end if;')
s=s.replace("item.put('planning_basis','CONFIGURED_NORMS_ESTIMATE');", "if v_code in('DRIVE','DRIVE_BACK')then item.put('planning_basis',v_route_basis);else item.put('planning_basis','CONFIGURED_NORMS_ESTIMATE');end if;")
root=Path("db/migrations/2026-10-11_ni081_route_input")
out={str(root/"003_operation_api.sql"):s,
 str(root/"apply.sql"):"@@001_schema.sql\n@@002_source.sql\n@@003_operation_api.sql\n@@004_api.sql\n",
 str(root/"rollback.sql"):"-- Explicit recovery only; preserve/export route journal before removing metadata.\n@@../2026-10-10_ni081_operation_plan/001_api.sql\ndrop trigger RRL_TT_ROUTE_INPUT_GUARD;\ndrop package RRL_TT_ROUTE_API;\ndrop package RRL_TT_ROUTE_SOURCE;\n-- Retain RRL_TT_ROUTE_INPUT history until explicit data disposal.\n",
 str(root/"verify.sql"):"select object_name,object_type,status from user_objects where object_name in('RRL_TT_ROUTE_SOURCE','RRL_TT_ROUTE_API','RRL_TT_OPERATION_PLAN_API','RRL_TT_ROUTE_INPUT_GUARD');\nselect name,type,line,text from user_errors where name in('RRL_TT_ROUTE_SOURCE','RRL_TT_ROUTE_API','RRL_TT_OPERATION_PLAN_API','RRL_TT_ROUTE_INPUT_GUARD');\n"}
print(json.dumps(out,ensure_ascii=True))
