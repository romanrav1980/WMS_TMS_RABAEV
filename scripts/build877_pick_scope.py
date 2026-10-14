from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
root=read("tmp/876_root_body.sql");access=read("tmp/876_access_body.sql")
old="if g_kind='WAVE_EXECUTION_FINISH'then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;"
assert root.count(old)==2
newroot=root.replace(old,"if g_kind in('WAVE_EXECUTION_FINISH','WAVE_PICK_RELEASE')then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;")
old="if d.get_string('command_type')!='WAVE_EXECUTION_FINISH'then return;end if;"
assert access.count(old)==1
newaccess=access.replace(old,"if d.get_string('command_type')not in('WAVE_EXECUTION_FINISH','WAVE_PICK_RELEASE')then return;end if;")
needle="  assert_scope(wave,p_actor,'pick_wave_launch');"
assert newaccess.count(needle)==1
newaccess=newaccess.replace(needle,needle+"\n  if d.get_string('command_type')='WAVE_PICK_RELEASE'then return;end if;",1)
mid="2026-10-13-877-ni033-pick-current-scope";d="db/migrations/2026-10-13_ni033_pick_scope/"
files={d+"000_before_root.sql":root,d+"000_before_access.sql":access,d+"001_access.sql":newaccess,d+"002_root.sql":newroot,d+"003_ledger.sql":f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing pick release checks active actor/current warehouse before replay and after root resource locks',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",d+"apply.sql":"@@001_access.sql\n@@002_root.sql\n@@003_ledger.sql\n",d+"rollback.sql":f"@@000_before_root.sql\n@@000_before_access.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",
d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_POSTING_API','RRL_WAVE_EXEC_ACCESS');\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_POSTING_API','RRL_WAVE_EXEC_ACCESS');\n",
d+"checkpoint.json":json.dumps({"migration_id":mid,"state":"PREPARED","target":"RABAEV/orcl","before_sha256":{"root":hashlib.sha256(root.encode()).hexdigest(),"access":hashlib.sha256(access.encode()).hexdigest()},"after_sha256":{"root":hashlib.sha256(newroot.encode()).hexdigest(),"access":hashlib.sha256(newaccess.encode()).hexdigest()}},indent=2)}
files["wiki/database/nicora_ni033_pick_scope_20261013.md"]="""# NI03.3: текущий склад при допуске отбора

877 prepared, current Root/access captured876, SHA/paired rollback. Единственный stock writer ACTIVE unchanged; Root меняется только в двух existing access call predicates. До prepare/replay и после resource lock вызывается существующий RRL_WAVE_EXEC_ACCESS.assert_command также для WAVE_PICK_RELEASE. Helper проверяет active RUSERS/current WARE/GLOBAL_ADMIN/current pick_wave_launch. Для PICK не применяются disposition правила FINISH.

API pick-readiness теперь передаёт authenticated actor и читает native snapshot с assert_wave_view в одной READ ONLY транзакции. UI не является проверкой склада. Native20882 mapped403, а не общая409. Поля/rights semantics не расширяются, новый native command/policy/global lock не создаётся.

Это access fix текущего допуска; не полное испытание гонки изменения RUSERS/rights admin. Native source/current actor positive/foreign denial/replay и compile ожидают. [SQL](../../db/migrations/2026-10-13_ni033_pick_scope/apply.sql).
"""
p="wiki/index.md";files[p]="- [NI03.3 pick-scope877](database/nicora_ni033_pick_scope_20261013.md): prepared reuse current WAVE access/readonly preview; actual pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 prepared877 current pick scope: API actor readonly native view guard, two Root existing assert predicates + existing access helper for pick release. Current capture876/SHA/paired rollback; no quantity logic/lock topology change. Live/case pending.\n"
print(json.dumps(files,ensure_ascii=True))
