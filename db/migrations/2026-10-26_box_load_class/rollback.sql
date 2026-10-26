whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
declare s varchar2(4000);st varchar2(20);v varchar2(20);n number;begin select SEARCH_CONDITION_VC,STATUS,VALIDATED into s,st,v from USER_CONSTRAINTS where TABLE_NAME='RRL_PALLET_TYPE'and CONSTRAINT_NAME='RRL_PALLET_TYPE_CHK1';if regexp_replace(upper(s),'[[:space:]]','')!=regexp_replace(upper(q'~LOAD_UNIT_CLASS in ('PALLET', 'TROLLEY', 'CONTAINER', 'BOX')~'),'[[:space:]]','')or st!='ENABLED'or v!='VALIDATED'then raise_application_error(-20999,'CLASS_CONSTRAINT_DRIFT');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
declare n number;begin select count(*)into n from RRL_PALLET_TYPE where LOAD_UNIT_CLASS='BOX';if n!=0 then raise_application_error(-20999,'BOX_ROWS_EXIST_KEEP_ADDITIVE_CLASS');end if;end;
/
alter table RRL_PALLET_TYPE add constraint RRL_PT_CLASS_OLD_TMP check (LOAD_UNIT_CLASS in ('PALLET', 'TROLLEY', 'CONTAINER'));
alter table RRL_PALLET_TYPE drop constraint RRL_PALLET_TYPE_CHK1;
alter table RRL_PALLET_TYPE rename constraint RRL_PT_CLASS_OLD_TMP to RRL_PALLET_TYPE_CHK1;
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-26-box-load-class';
commit;
