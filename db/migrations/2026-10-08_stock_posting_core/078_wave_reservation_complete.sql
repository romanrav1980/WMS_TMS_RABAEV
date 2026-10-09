declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME like 'RRL_STOCK_%' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'WAVE_RESERVATION_PACKAGES_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-033-wave-source-reservation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Atomic replenishment source selection/HARD materialization in existing wave rows, physical unit allocation and reservation metadata',sysdate,user,'078_wave_reservation_apply.sql','078_wave_reservation_rollback.sql','APPLIED');
commit;
