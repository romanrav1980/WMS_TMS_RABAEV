alter table RRL_ACCESS_ASSIGNMENT drop constraint RRL_ACCESS_ASSIGN_USER_FK;
drop index RUSERS_ACTIVE_LOGIN_UK;
alter table RUSERS drop constraint RUSERS_ID_UK keep index;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-rusers-identity-constraints';
commit;
