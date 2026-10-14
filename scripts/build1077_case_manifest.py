from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_place_selection/";files={}
p=d+"002_place_read.sql";t=Path(p).read_text(encoding="utf-8")
t=t.replace("package RRL_ST_DEFER_WAIT_API)as", "package RRL_ST_DEFER_WAIT_API,package RRL_ST_DEFER_CASE_WAIT)as")
t=t.replace("items.put(i,item);","items.put(i,item,true);")
files[p]=t
p=d+"005_wait_api.sql";t=Path(p).read_text(encoding="utf-8")
needle="from_cell:=child.get_string('cell');case_uid:=child.get_string('pallet_identifier');case_version:=child.get_number('content_version');case_body:=child.to_clob;"
assert t.count(needle)==1
t=t.replace(needle,"child.put('cohort_manifest',RRL_ST_DEFER_PLACE_READ.manifest(decision.ST_NUMBER));\n     "+needle)
files[p]=t
case=Path("tmp/1077_rrl_st_defer_case_wait_package_body.sql").read_bytes().decode("utf-8").replace("\r\n","\n")
files[d+"000_before_case_cohort.sql"]=case
needle="  src clob;n number;target varchar2(50);";assert case.count(needle)==1
case=case.replace(needle,needle+"stored json_object_t;stored_wire clob;frozen_members json_array_t;current_members json_array_t;")
needle="  if dbms_lob.compare(src,p.SOURCE_MEMBERS_JSON)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE source');end if;"
assert case.count(needle)==1
replacement="""  stored:=json_object_t.parse(p.SOURCE_MEMBERS_JSON);
  if stored.has('cohort_manifest')then
   frozen_members:=stored.get_array('cohort_manifest');stored.remove('cohort_manifest');
   current_members:=RRL_ST_DEFER_PLACE_READ.manifest(dec.ST_NUMBER);
   if dbms_lob.compare(frozen_members.to_clob,current_members.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred ST membership/cargo');end if;
  end if;
  stored_wire:=stored.to_clob;
  if dbms_lob.compare(src,stored_wire)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: deferred CASE source');end if;"""
case=case.replace(needle,replacement)
needle="  p_current:=json_object_t.parse(src);p_current.put('decision',dec.OPERATION_ID);";assert case.count(needle)==1
case=case.replace(needle,"  p_current:=json_object_t.parse(src);if frozen_members is not null then p_current.put('cohort_manifest',current_members);end if;p_current.put('decision',dec.OPERATION_ID);")
files[d+"010_case_cohort.sql"]=case
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8").replace("@@007_compile.sql","@@010_case_cohort.sql\n@@007_compile.sql")
p=d+"rollback.sql";files[p]=Path(p).read_text(encoding="utf-8").replace("drop package RRL_ST_DEFER_PLACE_READ;", "@@000_before_case_cohort.sql\ndrop package RRL_ST_DEFER_PLACE_READ;")
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="PREPARED";v["case_manifest"]="capture1077, no openwaitingplans atbaseline; newCASE sourcecohortmanifest guardsSTmembership/cargo without siblingversions; old sources compatible"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/retailcase_ni072_place_selection_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1077 PREPARED: collect array update uses explicit overwrite, CASE also freezes globalSTmembership/cargo while excluding siblingphysicalversions; originalnoManifest plans compatible. FreshCaseBody1077/no openWAITbaseline captured beforeapply. No secondwriter; plannedcase source uses oldCASE handler.\n"
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1077 PREPARED same selected-root manifest for CASE/HU, arrayoverwrites explicit, originalCASEbodycaptured/no openWAITbaseline; current source factories unchanged, apply pending.\n"
p="wiki/index.md";files[p]="- [CASE cohort1077](database/retailcase_ni072_place_selection_20261013.md): prepared currentmembership/cargo proof for bothHU/CASE, compatibleoldmanifestlessplans, no openWAITbaseline.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
