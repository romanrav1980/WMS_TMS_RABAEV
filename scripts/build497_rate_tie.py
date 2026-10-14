import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=Path("db/migrations/2026-10-12_ni071_rate_revision");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select text from user_source where name='RRL_LOG_COST_LINE_GUARD'and type='TRIGGER'order by line")
 src="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
 old="order by h.EFFECTIVE_FROM desc fetch first 1 row only"
 assert src.count(old)==1
 out[str(d/"000_before_guard.sql")]=src
 out[str(d/"001_guard.sql")]=src.replace(old,"order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 row only")
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_costs.py");s=p.read_text(encoding="utf-8")
assert s.count(old)==1;s=s.replace(old,"order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 row only");out[str(p)]=s
out[str(d/"apply.sql")]="@@001_guard.sql\n@@002_ledger.sql\n"
out[str(d/"rollback.sql")]="@@000_before_guard.sql\n-- Restore Python rate selector together; posted historical costs remain immutable.\n"
out[str(d/"002_ledger.sql")]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-497-same-day-rate-revision' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Deterministic latest version for same-effective-day warehouse rate; original frozen costs preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');\n/\n"
print(json.dumps(out))
