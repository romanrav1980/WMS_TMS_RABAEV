from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_recovery_consolidation");out={}
out[(d/"001_key.sql").as_posix()]="""declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_IW_RECOVERY_DISPATCH'and CONSTRAINT_NAME='RRL_IW_REC_DISPATCH_PK';
 if n=0 then execute immediate 'alter table RRL_IW_RECOVERY_DISPATCH drop constraint SYS_C0018245';execute immediate 'alter table RRL_IW_RECOVERY_DISPATCH add constraint RRL_IW_REC_DISPATCH_PK primary key(OPERATION_ID,ST_ID)';end if;
end;
/
"""
t=(d/"000_before_next.sql").read_text(encoding="utf-8")
t=t.replace("utl_i18n.string_to_raw(op,'AL32UTF8')","utl_i18n.string_to_raw(op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_st),'AL32UTF8')")
out[(d/"002_next.sql").as_posix()]=t
t=(d/"000_before_ship.sql").read_text(encoding="utf-8")
t=t.replace("    if subdomain.get_object('interwarehouse_onward_source').has('recovery_operation_id')then raise_application_error(-20886,'INTERWARE_MULTI_RECOVERY_EXPLICIT_LINEAGE_REQUIRED');end if;\n","")
out[(d/"003_ship.sql").as_posix()]=t
out[(d/"004_dispatch_guard.sql").as_posix()]="""create or replace trigger RRL_IW_REC_DISPATCH_GUARD before insert or update or delete on RRL_IW_RECOVERY_DISPATCH for each row
declare n number;begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_DISPATCH_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_DISPATCH',:new.OPERATION_ID));
 select count(*)into n from RRL_IW_RECOVERY_ST_BIND b join RRL_INTERWARE_RECOVERY_RECEIPT r on r.OPERATION_ID=b.RECOVERY_OPERATION_ID
 join RRL_IW_RECOVERY_PLACEMENT p on p.RECOVERY_OPERATION_ID=r.OPERATION_ID
 where b.OPERATION_ID=:new.BIND_OPERATION_ID and b.ST_ID=:new.ST_ID and b.ROOT_UID=:new.ROOT_UID
 and b.RECOVERY_OPERATION_ID=:new.RECOVERY_OPERATION_ID and b.RECEIPT_OPERATION_ID=:new.RECEIPT_OPERATION_ID
 and b.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID
 and r.BASE_QTY=:new.BASE_QTY and r.BASE_UOM=:new.BASE_UOM and p.TARGET_CELL=b.SOURCE_CELL;
 if n!=1 then raise_application_error(-20886,'RECOVERY_DISPATCH_EXACT_LINEAGE_REQUIRED');end if;
end;
/
"""
out[(d/"005_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_marked_consolidation/004_recompile.sql").read_text()
out[(d/"006_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-367-recovery-consolidated-dispatch' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Original corrective ST/HU loading reused with perST dispatch keys and exact recovered lineage, no second fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="".join("@@"+f+"\n"for f in ["001_key.sql","002_next.sql","003_ship.sql","004_dispatch_guard.sql","005_recompile.sql","006_ledger.sql"])
out[(d/"rollback.sql").as_posix()]="""declare n number;begin select count(*)into n from(select OPERATION_ID from RRL_IW_RECOVERY_DISPATCH group by OPERATION_ID having count(*)>1);if n>0 then raise_application_error(-20899,'CONSOLIDATED_RECOVERY_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_next.sql
@@000_before_ship.sql
alter table RRL_IW_RECOVERY_DISPATCH drop constraint RRL_IW_REC_DISPATCH_PK;
alter table RRL_IW_RECOVERY_DISPATCH add constraint SYS_C0018245 primary key(OPERATION_ID);
"""
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_IW_RECOVERY_NEXT','RRL_STOCK_HU_SHIP_CMD','RRL_IW_REC_DISPATCH_GUARD');\nselect OPERATION_ID,count(*)from RRL_IW_RECOVERY_DISPATCH group by OPERATION_ID having count(*)>1;\n"
print(json.dumps(out))
