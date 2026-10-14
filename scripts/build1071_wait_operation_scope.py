from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_nested_hu_wait/";files={}
t=Path(d+"018_already_waiting_api.sql").read_text(encoding="utf-8")
needle="  if n!=1 then raise_application_error(-20882,'DEFER_WAIT_CURRENT_WAREHOUSE_PLANNER_REQUIRED');end if;"
assert t.count(needle)==2
# Check within the existing exclusive metadata fence, after current actor validation.
pos=t.index(needle,t.index("RRL_STOCK_METADATA_TX.begin_change"))+len(needle)
guard="""
  select count(*)into n from RRL_STOCK_OPERATION op where op.OPERATION_ID=p_operation
   and not exists(select 1 from RRL_ST_DEFER_WAIT_RUN run where run.OPERATION_ID=p_operation);
  if n>0 then raise_application_error(-20886,'DEFER_WAIT_OPERATION_PAYLOAD_CONFLICT');end if;
"""
files[d+"019_wait_operation_scope.sql"]=t[:pos]+guard+t[pos:]
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@019_wait_operation_scope.sql\n"
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_VALID_METADATA_OPERATION_GUARD_PREPARED"
v["operation_scope_guard"]="1071 within metadata exclusive fence, do not reuse unrelated stock operation ID for no-move result"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1071 PREPARED: already-waiting metadata branch also refuses an existing unrelated RootoperationID after acquiring metadata exclusive fence (pre-check alone would race). ExistingRoot+WAIT_RUN cache retained; no reuse of HU_CREATE/stock posting ID as no-move receipt.\n"
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1071 prepared under-fence Rootoperation collision guard for metadataalreadywaiting; invariant sameoperationdifferentpayload cannot create another result, originalRoot+WAITcache unchanged.\n"
p="wiki/index.md";files[p]="- [Operation scope1071](database/nicora_ni072_nested_hu_wait_20261013.md): under-fence metadata/RootID collision guard prepared, currentnestedruntime preserved.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
