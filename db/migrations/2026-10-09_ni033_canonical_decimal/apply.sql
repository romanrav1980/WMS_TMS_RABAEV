@@001_helper.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare s varchar2(200);begin
 s:=RRL_STOCK_PLAN_HELPER.decimal_text(0.3);
 if s!='0.3' or RRL_STOCK_MATH.quantity(s)!=0.3 then raise_application_error(-20808,'CANONICAL_FRACTION_INVALID');end if;
 if RRL_STOCK_PLAN_HELPER.decimal_text(-0.3)!='-0.3' then raise_application_error(-20808,'CANONICAL_SIGNED_FRACTION_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-033-canonical-decimal' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Normalize Oracle TM9 leading fractional zero without rounding or relaxing input contract',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
