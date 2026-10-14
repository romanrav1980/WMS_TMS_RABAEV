from pathlib import Path
import json,re,hashlib
before=Path("tmp/868_shared_body.sql").read_text(encoding="utf-8")
after=re.sub(r"\n[ \t\r]*\n(?:[ \t\r]*\n)+","\n\n",before).replace('v_duplicates number;','v_source_owned number;')
after=after.replace('select count(*) into v_duplicates from RRL_STOCK_RESERVATION','select nvl(sum(BASE_QTY),0) into v_source_owned from RRL_STOCK_RESERVATION')
after=after.replace('   if v_duplicates!=1 then return 0;end if;','   -- Separate bindings of the same owner share one physical source.\n   -- Admission compares their total quantity, without merging their identities.')
after=after.replace('if sr.BASE_QTY>greatest(0,v_remaining-v_target_owned)','if v_source_owned>greatest(0,v_remaining-v_target_owned)')
assert 'v_duplicates'not in after
d="db/migrations/2026-10-13_ni032_shared_bindings/";mid="2026-10-13-869-ni032-shared-bindings"
files={d+"000_before_shared.sql":before,d+"001_shared.sql":after,
d+"002_ledger.sql":f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Shared whole-pallet admission checks total per-owner source bindings against unmet target demand',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",d+"apply.sql":"@@001_shared.sql\n@@002_ledger.sql\n",d+"rollback.sql":f"@@000_before_shared.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",
d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_REPL_SHARED';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_REPL_SHARED';\n",
d+"checkpoint.json":json.dumps({"migration_id":mid,"state":"PREPARED","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_sha256":hashlib.sha256(after.encode()).hexdigest(),"target":"RABAEV/orcl"},indent=2)}
p=Path("wiki/database/nicora_ni032_same_source_bindings_20261013.md")
files[str(p)]=p.read_text(encoding="utf-8")+"""\n## Допуск869

866 applied VALID; fresh867 остановился до physical issuance, finally owncleanup. Старый RRL_STOCK_REPL_SHARED.allowed также запрещал несколько source bindings одного CASE owner.869 prepared: count=1 заменён sum(BASE_QTY) per current UID/cell/wave/line against remaining minus existing target HARD. Каждый distinct reservation проходит прежний warehouse/target/CASE/status/customer check; исходный полный ordered transfer closure сохраняется. Не объединяет reservations, не списывает чужой товар. Captured868/SHA/paired rollback. Повторный свежий case и live verification ожидают.
"""
p=Path("wiki/index.md");files[str(p)]="- [NI03.2 shared-binding869](database/nicora_ni032_same_source_bindings_20261013.md): prepared aggregate admission;866 VALID, failed867 before physical issuance/owncleanup.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 prepared869: captured868 shared owner admission, per-source own sum rather than count1;866VALID but867 correctly refused old shared guard, no pass claim, owncleanup. Native apply/fresh retry pending.\n"
print(json.dumps(files,ensure_ascii=True))
