@@001_hop_guard.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_INTERWARE_HOP_LIMIT_GUARD'and STATUS='VALID';if n!=1 then raise_application_error(-20899,'INTERWARE123_INVALID_HOP_GUARD');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-123-original-order-final-delivery-lineage' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Bounded original customer read-only receipt lineage through final second shoulder; multi-hop requires explicit ownership support',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
