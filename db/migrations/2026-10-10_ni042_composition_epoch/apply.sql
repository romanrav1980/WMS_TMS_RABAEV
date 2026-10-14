@@001_schema.sql
@@002_invariant_decoder.sql
@@003_context.sql
@@004_unit_signature.sql
@@005_composition_core.sql
@@006_root.sql
@@007_qc_gate.sql
@@008_guard.sql
@@009_case_birth.sql
@@010_task_birth.sql
@@011_mes_birth.sql
@@012_move_birth.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_COMPOSITION_CORE','RRL_STOCK_POSTING_API','RRL_STOCK_QC_GATE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'COMPOSITION_EPOCH_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-073-stock-composition-epoch' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Per-UID composition epoch finalized once per root for total P or physical member changes; intact same-UID movement/HARD preserves; QC v2 prevents restoration resurrection',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
