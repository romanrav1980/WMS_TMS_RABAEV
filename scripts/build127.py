from pathlib import Path
import json,re
out={};dest="db/migrations/2026-10-10_ni043_mes_scope/"
s=Path("db/migrations/2026-10-08_stock_posting_core/442_before127_mes_movement_core.sql").read_text(encoding="utf-8")
# Keep existing spec and body for the maintained current-source contract bundle.
needle="  if o.STATUS='CANCELLED' then"
assert needle in s
s=s.replace(needle,"""  select count(*)into v_n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=o.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if v_n!=1 then raise_application_error(-20882,'MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED');end if;
"""+needle,1)
out[dest+"001_core.sql"]=s
out[dest+"apply.sql"]="""@@001_core.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_MES_MOVEMENT_CORE'and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'MES127_INVALID_CORE');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-127-mes-current-warehouse-scope' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Current MES actor warehouse scope enforced inside existing sole native stock writer','SYSDATE',user,'apply.sql','rollback.sql','APPLIED');
commit;
/
""".replace("'SYSDATE'","sysdate")
out[dest+"rollback.sql"]="""begin raise_application_error(-20899,'MES127_SCOPE_SAFETY_FORWARD_ONLY');end;
/ 
"""
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py");s=p.read_text(encoding="utf-8")
needle='    if sum(len(values) for values in request.units_by_movement.values()) > 10000:'
assert needle in s
s=s.replace(needle,"""    scope=gateway.fetch_all("select 1 ALLOWED from RRL_PRODUCTION_ORDER p where p.PRODUCTION_ORDER_ID=:order_id and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=p.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'))",{"order_id":production_order_id,"actor":actor})
    if len(scope)!=1:
        raise HTTPException(403,detail={"code":"MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED","operation_id":request.operation_id,"outcome_confirmed":True})
"""+needle,1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
