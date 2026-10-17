declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20886,'WARES_KEY_WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WARES_KEY_INVALID_BEFORE');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'WARES_KEY_ERRORS_BEFORE');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-wares-identity-keys';if n!=0 then raise_application_error(-20886,'WARES_KEY_LEDGER_EXISTS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_WARES'and CONSTRAINT_TYPE in('P','U');if n!=0 then raise_application_error(-20886,'WARES_KEY_REVIEW_EXISTING_KEYS');end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME in('RRL_WARES_PK','RRL_WARES_NAME_UK','RRL_WARES_NAME_NN');if n!=0 then raise_application_error(-20886,'WARES_KEY_CONSTRAINT_COLLISION');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WARES_PK','RRL_WARES_NAME_UK');if n!=0 then raise_application_error(-20886,'WARES_KEY_OBJECT_COLLISION');end if;
 select count(*)into n from USER_IND_COLUMNS where TABLE_NAME='RRL_WARES'and COLUMN_POSITION=1 and COLUMN_NAME in('ID','NAME');if n!=0 then raise_application_error(-20886,'WARES_KEY_LEADING_INDEX_DRIFT');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WARES'and COLUMN_NAME in('ID','NAME')and NULLABLE='Y';if n!=2 then raise_application_error(-20886,'WARES_KEY_NULLABILITY_DRIFT');end if;
 select count(*)into n from RRL_WARES where ID is null or ID<=0 or ID!=trunc(ID)or NAME is null;if n!=0 then raise_application_error(-20886,'WARES_KEY_INVALID_DATA');end if;
 select count(*)into n from(select ID from RRL_WARES group by ID having count(*)>1);if n!=0 then raise_application_error(-20886,'WARES_KEY_DUPLICATE_ID');end if;
 select count(*)into n from(select NAME from RRL_WARES group by NAME having count(*)>1);if n!=0 then raise_application_error(-20886,'WARES_KEY_DUPLICATE_NAME');end if;
end;
/
