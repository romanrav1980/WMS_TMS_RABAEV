import json
from pathlib import Path
d="db/migrations/2026-10-14_ni033_pick_article_identity/"
mid="2026-10-14-1248-pick-article-identity"
files={
d+"apply.sql":"@@001_picking.sql\n@@002_ledger.sql\n",
d+"rollback.sql":"@@000_before.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='"+mid+"';\n/\n",
d+"verify.sql":"select OBJECT_NAME,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_PICKING_API';\nselect LINE,POSITION,TEXT from USER_ERRORS where NAME='RRL_PICKING_API' order by SEQUENCE;\n",
d+"002_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '"""+mid+"""' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Preserve exact canonical article in ACTIVE pick planning; exact source matching; no stock rewrite',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",
"wiki/database/retailcase_ni033_pick_article_identity_20261014.md":"""# NI03.3: точный артикул в плане отбора

Миграция: 2026-10-14-1248-pick-article-identity. Подготовлена; результат применения будет добавлен после исполнения.

При запуске волны558 на резерве плана2190 обнаружено WAVE_BASE_POLICY_REQUIRED: планировщик превращал артикул QAUTOc0c2a00c0bA в QAUTOC0C2A00C0BA. Карточка, единицы и физическая паллета сохраняют исходный идентификатор.

В ACTIVE-режиме RRL_PICKING_API сохраняет точный артикул строки заказа в строках плана, заданиях, резервах и дефиците; кандидатная паллета должна иметь тот же точный артикул. Legacy-режим сохраняет прежнее поведение. UPPER не используется как способ объединить разные карточки в новом ядре. Admission может блокировать более широкий набор кандидатов; это не разрешает отбор другой карточки.

Ошибочный ещё не запущенный план отменяется существующими командами с сохранением истории, после чего создаётся новый. Прямой правки резервов, остатков или справочника единиц нет. Сохранённый результат старого operation_id не переписывается.

[SQL и исходный пакет](../../db/migrations/2026-10-14_ni033_pick_article_identity/). Исходный package body и список INVALID сохранены до изменения; apply/rollback/verify включены. Локальный файловый checkpoint вместо публикации/копирования базы соответствует разрешённому dev-переходу. Полная копия Oracle не создаётся.
""",
}
for file,addition in {
"wiki/index.md":"- [Точный артикул в плане1248](database/retailcase_ni033_pick_article_identity_20261014.md): подготовлена коррекция UPPER в существующем планировщике; волна558 остановлена до проведения.\n",
"wiki/log.md":"\n## 2026-10-14 · 1248 · идентификатор товара\nПодготовлена исправляющая миграция существующего RRL_PICKING_API: точный артикул в ACTIVE, без слияния карточек и прямого изменения остатков. Исходный пакет и INVALID checkpoint сохранены. Причина обнаружена на волне558/плане2190; применение и повтор исполнения ещё не подтверждены.\n",
}.items():
 old=Path(file).read_text(encoding="utf-8")
 files[file]=addition+old if file.endswith("index.md")else old+addition
print(json.dumps(files,ensure_ascii=True))

