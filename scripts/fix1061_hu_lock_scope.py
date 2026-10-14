from pathlib import Path
import json,hashlib,re
d="db/migrations/2026-10-13_ni072_nested_hu_wait/";files={}
t=Path(d+"012_hu_wire.sql").read_text(encoding="utf-8")
t=re.sub(r'\bst_number\b','v_st_number',t)
# Restore JSON property names; only PL/SQL scalar is renamed.
t=t.replace("'v_st_number'","'st_number'")
t=t.replace(" where ID=trip for update;", " where ID=trip for update nowait;")
t=t.replace(" where ID=x.ID for update;", " where ID=x.ID for update nowait;")
t=t.replace("cases json_array_t;item json_object_t;trip number;st number;v_st_number varchar2(100);", "cases json_array_t;item json_object_t;trip number;st number;v_st_number varchar2(100);row_busy exception;pragma exception_init(row_busy,-54);")
# Handle only the source-row validation procedure's exception, with a retryable stock lock code.
needle="  end if;\n end;\nend;\n/";assert t.count(needle)==1
t=t.replace(needle,"  end if;\n exception when row_busy then raise_application_error(-20840,'LOCK_RETRY: deferred HU source rows busy');\n end;\nend;\n/")
files[d+"013_hu_lock_scope.sql"]=t
case=Path(d+"002_case_scope.sql").read_text(encoding="utf-8")
# Rename the local ancestry identifiers so CHILD_PALLET_UID compares with a scalar rather than PARENT_UID column.
case=re.sub(r'\bparent_uid\b','v_parent_uid',case,flags=re.IGNORECASE)
# Restore SQL column occurrences, which are uppercase in the captured source and replacement.
case=case.replace("min(v_parent_uid)","min(PARENT_UID)")
# Parent variable in declaration and query RHS remains v_parent_uid.
files[d+"014_case_parent_scalar.sql"]=case
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@013_hu_lock_scope.sql\n@@014_case_parent_scalar.sql\n@@009_compile.sql\n"
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_VALID_LOCK_SCOPE_CORRECTION_PREPARED"
v["lock_correction"]="1061 timeout trial/no committed plan: ST_NUMBER scalar shadowed column; rename scalar, NOWAIT exact source rows ->retryable20840; ancestry scalar also renamed"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/retailcase_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1061: plan trial timed out before commit because unqualified ST_NUMBER scalar resolved as the table column in locked ST cursor. Correct013 uses v_st_number, exact source rows and NOWAIT→retryable20840. CASE ancestry parent scalar also renamed in014 to distinguish PARENT_UID column, preserving true multi-level roots. Only PACKED retainedsource persists, no newstockbirth. Not accepted until corrected actualplan/move.\n"
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1061: actual HU plan timeout found SQL scalar/column shadowing in ST locked cursor. No committedplan/stock; captured correction013 exactST+NOWAIT and014 ancestry scalar checkpointed before apply.\n"
p="wiki/index.md";files[p]="- [Lock-scope1061](database/retailcase_ni072_nested_hu_wait_20261013.md): exact ST scalar/NOWAIT20840 and ancestor scalar correction prepared after timeout/no commit.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
