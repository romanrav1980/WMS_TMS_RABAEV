-- Root-only recovery before any dependent FK. Never CASCADE or remove foreign history.
@@verify.sql
declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_TYPE='R'and R_OWNER=user and R_CONSTRAINT_NAME in('RRL_WARES_PK','RRL_WARES_NAME_UK');
 if n!=0 then raise_application_error(-20886,'WARES_KEY_DEPENDENT_FOREIGN_KEYS_FORWARD_ONLY');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-wares-identity-keys'and STATUS='APPLIED';if n!=1 then raise_application_error(-20886,'WARES_KEY_APPLIED_LEDGER_REQUIRED');end if;
end;
/
alter table RRL_WARES drop constraint RRL_WARES_NAME_UK;
alter table RRL_WARES drop constraint RRL_WARES_NAME_NN;
alter table RRL_WARES drop constraint RRL_WARES_PK;
declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME in('RRL_WARES_PK','RRL_WARES_NAME_UK','RRL_WARES_NAME_NN');if n!=0 then raise_application_error(-20886,'WARES_KEY_ROLLBACK_CONSTRAINTS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WARES_PK','RRL_WARES_NAME_UK');if n!=0 then raise_application_error(-20886,'WARES_KEY_ROLLBACK_INDEXES');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WARES'and COLUMN_NAME in('ID','NAME')and NULLABLE='Y';if n!=2 then raise_application_error(-20886,'WARES_KEY_ROLLBACK_NULLABILITY');end if;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-wares-identity-keys'and STATUS='APPLIED';
commit;
