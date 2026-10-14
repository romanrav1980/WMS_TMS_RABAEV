from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni033_case_start_instant")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text())
for key,file in [("startup_scripts","001_columns.sql"),("additional_scripts","002_guard.sql")]:
 value="../"+d.name+"/"+file
 if value not in m[key]:m[key].append(value)
cols=m["required_columns"].setdefault("RRL_CASE_PICK_TASK",[])
for col in ["STARTED_AT_INSTANT","STARTED_SHIFT_TIME_ZONE"]:
 if col not in cols:cols.append(col)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni033_case_start_instant_20261012.md"
out[page]="""# Точный момент начала сборки CASE
Миграция2026-10-12-361-case-actual-aware-start APPLIED dev RABAEV/orcl. Existing CaseActions.start_task записывает STARTED_AT_INSTANT TIMESTAMP WITH TIME ZONE вместе с прежним началом, назначением и STARTED event в той же metadata transaction/ordered CONFIG6. Повтор сохраняет первый момент и один event. Guard запрещает импорт выдуманного начала, изменение первого момента, backfill старого naive STARTED_AT и запись пояса без достоверного источника.

RRL_RESOURCE_SHIFT.START_AT/FINISH_AT — TIMESTAMP(6) без пояса. Поэтому STARTED_SHIFT_TIME_ZONE пока NULL, включая назначенные смены. Physical ZONE_CODE не является часовым поясом. Старые времена не интерпретируются как UTC или местные. Для выбора рабочего дня необходима явная политика пояса склада.

Actual361: собственное пустое CASE с отдельным типом тары, штатный COUNT1/BOOK, existing start/currentserver with Oracle offset, repeated start/one event, immutable guard, transaction rollback. Python Oracle thin fetch datetime не сохраняет tzinfo; доказательство offset получено Oracle TO_CHAR(TZH:TZM), а не предположением Python. После проверки BOOK_CANCEL/COUNT0, пустая fixture metadata отмечена CANCELLED. Обычный empty-return отказал CASE_EMPTY_CANCEL_LINE_BOUND_1_200 из-за отсутствия строк; это не объявляется успешной бизнес-отменой. Товар не создавался, protected P20/H20 неизменны. Context tmp/context361.json; initial factory не повторять.

Период существующего BOX cost пока loaded UTC. Новое поле подготавливает достоверный источник начала; NS56 этим не закрыт.
"""
for file,text in [
 ("wiki/index.md","- [Точный момент начала CASE](database/retailcase_ni033_case_start_instant_20261012.md):361 same start/event/TSTZ/immutable/rollback; legacy shift zone unknown.\n"),
 ("wiki/log.md","\n- 12.10.2026 361 nativeCASE actual aware start/immutableclock/currentactor/tarebook/one event/repeat/rollback PASS; own emptyfixture book released/count0/metadata retired; historical shift timestamps naive, zone explicitly unknown/no backfill. Native bundle includes columns/guard; financial period still pending.\n"),
 ("wiki/runbooks/retailcase_active_work.md","\nCurrent361: CASE start native TSTZ and nullable unknown shift zone, positive old action under rollback/tare0/protected20. Source tmp/context361.json closed; initial factory forbidden. Next explicit warehouse operating time zone and safe assembly-period financial basis.\n"),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni03_3.md","\n361: existing CASE start stores immutable actual TSTZ, one event on repeat/rollback/currentactor/tare. Legacy naive starts cannot be guessed; assignedshift also naive so zone NULL. Explicit warehouse operating-day policy needed for finance.\n")]:
 p=Path(file);old=p.read_text(encoding="utf-8");out[file]=text+old if file=="wiki/index.md"else old+text
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI03.3/361_case_start_clock.md").as_posix()]="# Qwen361\nExisting CASE start with actual booked tare; first TSTZ immutable/repeat one event/rollback; old naive start no fabricated backfill. Assigned shift timestamps are naive, unknown zone must remain NULL. Own context361 retired/tare0/protected20; no initial factory rerun. Financial operating day still pending.\n"
p=Path("scripts/build361_case_start_time.py");t=p.read_text(encoding="utf-8");a=t.index(" if :new.RESOURCE_SESSION_ID is not null then");b=t.index(" if nvl(zone_text",a);t=t[:a]+t[b:];a=t.index("                   STARTED_SHIFT_TIME_ZONE = (select");b=t.index('",1)',a);t=t[:a]+"                   STARTED_SHIFT_TIME_ZONE = null,"+t[b:];t=t.replace("and original assigned shift zone","with unknown legacy shift zone kept NULL");out[p.as_posix()]=t
p=d/"004_ledger.sql";out[p.as_posix()]=p.read_text().replace("and original assigned shift zone","with unknown legacy shift zone kept NULL")
print(json.dumps(out))
