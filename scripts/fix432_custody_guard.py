from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_custody';p=Path('tmp/native431_load_guard.sql');t=p.read_text(encoding='utf-8')
needle="   if n!=1 then raise_application_error(-20863,'INTERWARE_ACTUAL_CUSTODY_PROOF_REQUIRED');end if;"
add="""   if n=0 then
    select count(*)into n from RRL_IW_GROUP_CUSTODY f join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID
    join RRL_IW_GROUP_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID join RRL_IW_GROUP_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID
    where f.OPERATION_ID=op and f.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and p.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID
    and r.ROOT_UID=:old.ROOT_UID and p.ROOT_UID=r.ROOT_UID and u.ROOT_UID=r.ROOT_UID and u.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID
    and :new.CUSTODY_RELEASED_AT=u.CREATED_AT;
   end if;
"""+needle
assert needle in t;t=t.replace(needle,add,1)
out={d+'/000_before_load_guard.sql':p.read_text(encoding='utf-8'),d+'/004a_load_guard.sql':t}
p=Path(d+'/apply.sql');out[p.as_posix()]=p.read_text(encoding='utf-8').replace('@@005_ledger.sql','@@004a_load_guard.sql\n@@005_ledger.sql')
p=Path(d+'/rollback.sql');out[p.as_posix()]=p.read_text(encoding='utf-8').replace('@@000_before_custody.sql','@@000_before_custody.sql\n@@000_before_load_guard.sql')
print(json.dumps(out))
