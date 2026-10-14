from pathlib import Path
p=Path('db/migrations/2026-10-14_ni051_scoped_quality/002_reader.sql');s=p.read_text(encoding='utf-8').replace("origin_ware number:=w;addr", "origin_ware number:=w;document_no number:=d.get_number('document_id');addr").replace("where ID=d.get_number('document_id');", "where ID=document_no;")
s=s.replace("proof json_object_t;payload clob;existing clob;", "proof json_object_t;payload clob;existing clob;document_no number:=d.get_number('document_id');")
s=s.replace("DOCUMENT_ID=d.get_number('document_id')", "DOCUMENT_ID=document_no").replace("values(op,d.get_number('document_id'),payload)", "values(op,document_no,payload)")
p.write_text(s,encoding='utf-8')
root=p.parent
(root/'apply.sql').write_text('''@@001_schema.sql
@@002_reader.sql
@@003_policy.sql
@@004_gate.sql
@@005_shipping.sql
@@006_quality.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-1447-ni051-scoped-quality' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped QC rules, versioned current policy and immutable whole-pallet exemption under original stock root',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
''',encoding='utf-8')
(root/'verify.sql').write_text('''declare n number;begin
 select count(*) into n from USER_ERRORS where NAME in('RRL_QC_SCOPE_READ','RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_PALLET_QC_CMD','RRL_QC_SCOPE_RULE_GUARD','RRL_QC_SCOPE_CHANGE_GUARD','RRL_QC_EXEMPT_FACT_GUARD');
 if n>0 then raise_application_error(-20808,'QUALITY_SCOPE_COMPILE_ERRORS');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_QC_SCOPE_READ','RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_PALLET_QC_CMD','RRL_QC_SCOPE_RULE_GUARD','RRL_QC_SCOPE_CHANGE_GUARD','RRL_QC_EXEMPT_FACT_GUARD') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'QUALITY_SCOPE_INVALID');end if;
end;
/
''',encoding='utf-8')
(root/'rollback.sql').write_text('''-- Restore code only; retain configuration history and posted exemption audit.
@@saved/RRL_STOCK_QC_POLICY_PACKAGE_BODY.sql
@@saved/RRL_STOCK_QC_GATE_PACKAGE_BODY.sql
@@saved/RRL_STOCK_SHIPPING_CORE_PACKAGE_BODY.sql
@@saved/RRL_STOCK_PALLET_QC_CMD_PACKAGE_BODY.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1447-ni051-scoped-quality';
commit;
/
''',encoding='utf-8')
import hashlib,json
files={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*.sql')}
(root/'checkpoint.json').write_text(json.dumps({'migration_id':'2026-10-14-1447-ni051-scoped-quality','files':files},indent=2),encoding='utf-8')
