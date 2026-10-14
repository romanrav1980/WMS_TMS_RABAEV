import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni071_transport_norms")
src=(d/"002_norm_api.sql").read_text(encoding="utf-8")
out={str(d/"000_before_auth_lock.sql"):src}
v=src.replace("head_ware number;effective date;","head_ware number;user_group_name varchar2(255);effective date;")
needle="  select count(*)into n from RUSERS u where u.ID=p_actor"
assert v.count(needle)==1
v=v.replace(needle,"""  -- Stable current actor/group/grant during row waits and saved-result replay.
  begin
   select USER_GROUP into user_group_name from RUSERS where ID=p_actor and nvl(DELETED,0)=0 for update;
  exception when no_data_found then raise_application_error(-20882,'TRANSPORT_NORM_CURRENT_FINANCE_REQUIRED');end;
  if upper(trim(user_group_name))!='GLOBAL_ADMIN'then
   n:=0;
   for grant_row in(select ID from RIGHTS where USER_GROUP=user_group_name and upper(trim(RIGHT1))='CREATE_TT_PRICE'order by ID for update)loop n:=n+1;end loop;
   if n=0 then raise_application_error(-20882,'TRANSPORT_NORM_CURRENT_FINANCE_REQUIRED');end if;
  end if;
"""+needle)
needle="  select *into price from RRL_TRANSPORT_PRICE where ID=price_id for update;"
assert v.count(needle)==1
v=v.replace(needle,"""  begin select *into price from RRL_TRANSPORT_PRICE where ID=price_id for update;
  exception when no_data_found then raise_application_error(-20886,'TRANSPORT_NORM_LEGACY_SOURCE_REQUIRED');end;""")
out[str(d/"004_auth_locks.sql")]=v
out[str(d/"005_auth_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-534-transport-norm-current-auth-locks' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Norm publication locks actor/grant then exact source/head; saved replay cannot outlive current rights',sysdate,user,'004_auth_locks.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply.sql")]="@@001_schema.sql\n@@002_norm_api.sql\n@@003_ledger.sql\n@@004_auth_locks.sql\n@@005_auth_ledger.sql\n"
out[str(d/"apply_auth_locks.sql")]="@@004_auth_locks.sql\n@@005_auth_ledger.sql\n"
print(json.dumps(out))
