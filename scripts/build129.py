from pathlib import Path
import json
out={};dest="db/migrations/2026-10-10_ni043_inventory_scope/"
for checkpoint,name in [("443_before129_inventory_birth.sql","001_birth.sql"),("444_before129_inventory_count.sql","002_count.sql")]:
 s=Path("db/migrations/2026-10-08_stock_posting_core/"+checkpoint).read_text(encoding="utf-8")
 needle="  if ware!=v.get_number('warehouse')"
 assert needle in s
 s=s.replace(needle,"""  declare actor_count number;begin
  select count(*)into actor_count from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if actor_count!=1 then raise_application_error(-20882,'INVENTORY_CURRENT_WAREHOUSE_ACTOR_REQUIRED');end if;
  end;
"""+needle,1)
 out[dest+name]=s
out[dest+"apply.sql"]="""@@001_birth.sql
@@002_count.sql
alter package RRL_STOCK_POSTING_API compile body;
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_INVENTORY_BIRTH','RRL_STOCK_INVENTORY_CMD','RRL_STOCK_POSTING_API')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INVENTORY129_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-129-inventory-current-warehouse-scope' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Current warehouse actor scope inside native inventory birth/count; existing sole posting kernel',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[dest+"rollback.sql"]="""begin raise_application_error(-20899,'INVENTORY129_SCOPE_SAFETY_FORWARD_ONLY');end;
/ 
"""
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .stock_posting_uow import StockPosting","from .stock_posting_uow import StockPosting\nfrom .inventory_scope import assert_inventory_scope",1)
s=s.replace("def lots(self, revision_id: int, cell: str, article: str | None) -> dict[str, Any]:","def lots(self, revision_id: int, cell: str, article: str | None, actor: str) -> dict[str, Any]:\n        assert_inventory_scope(self.gateway,actor,revision=revision_id)",1)
s=s.replace("def count(self, request: CountSubmission, actor: str) -> dict[str, Any]:","def count(self, request: CountSubmission, actor: str) -> dict[str, Any]:\n        assert_inventory_scope(self.gateway,actor,revision=request.revision_id)",1)
s=s.replace("def create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]:","def create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]:\n        assert_inventory_scope(self.gateway,actor,warehouse=warehouse_id)",1)
s=s.replace("def register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]:","def register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]:\n        assert_inventory_scope(self.gateway,actor,revision=revision_id)",1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_observations.py");s=p.read_text(encoding="utf-8").replace("def lots(self, revision_id: int, cell: str, article: str | None)","def lots(self, revision_id: int, cell: str, article: str | None, actor: str)",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py");s=p.read_text(encoding="utf-8").replace("return service.lots(revision_id,cell,article)","return service.lots(revision_id,cell,article,user.username)",1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
