# Исполнение до23:00 МСК ·15.10.2026

Работа остановлена по установленной владельцем границе23:00 МСК15.10.2026.
Все спринты **ещё не завершены**. Следующее начало — recovery scope инкремент
ниже; возобновление после этой границы требует нового поручения владельца.
Общий living checklist: [[retailcase_access_knowledge_plan]]. Изменения локальные,
публикация GitHub не поручена.

## Подтверждено в этом продолжении

- Складские названия (`ware_1` и другие) закреплены обязательным UNIQUE(NAME), числовой ID — PK для прежних связей.291 записи сохранены;4 FK учёта времени используют ID. [[../database/retailcase_wares_identity_keys_20261015]].
- Native CASE/TASK metadata abandon применён: immutable tombstone, текущие права и fence позднего original;8 caller-rollback и4 actual HTTP группы PASS. UI неизвестный результат сохраняет и связывает с исходной командой, help v3 опубликован. [[../database/retailcase_resource_metadata_intents_20261015]].
- Scoped ordinary CASE CLOSE применён. Изолированный CASE1139:1EA PICK, fresh-TX CLOSE, exact PICK/CLOSE replay, реальный HTTP exact CLOSE и changed-body409, RETURN caller-rollback затем canonical RETURN/cleanup PASS. [Неизменяемые намерения и результат](../../reports/retailcase/2026-10-15/n1939-positive-close/journal.json). Итог24/H0 в исходной ячейке: parent22+oldchild1+newchild1, lineage сохранён. CASE/волна/план отменены, session59 CLOSED, текущие grants отозваны; история остаётся. Полный RETURN admission сделан после PICK/CLOSE, ограничение заранее записано и не скрывается.
- Actual-time native источник применён:12 sources/80 constraints/4 warehouse FK/4 append-only guards/9 indexes/INVALID0. Отдельно исправлены verifier SYS_EXTRACT_UTC indexes и READ ISO parser, исходные неуспешные отчёты сохранены. Продолжение original intents PASS:8 events/10 commands/4 spans, OFF/IDLEv8. Это явный manual-source TEST, не полный KPI и не аппаратная активность. [Continuation](../../reports/retailcase/2026-10-15/picker-time-source/native-acceptance-continuation.json).
- Time UI хранит исходную команду по actor/origin, exact recovery и server UTC, help v3. Production native read/help на360/390/1440 PASS без бизнес-POST. Metadata recovery отдельно12 mocked checks; time26 pure/9 rendered и identity cancellation check. [[../components/retailcase_operator_ui_evidence_20261015]].
- HU tree показывает существующие native3nodes; мобильное меню и рабочая область уплотнены. Гант учитывает4семейства ресурсов и actual open CASE/shortage statuses; неполная readiness не становится зелёной. Тест видеопотока камеры реально проходит Chromium getUserMedia→video→canvas→ZXing→поле скана, но источник камеры синтетический, API mocked.
- Quality mass projection:37 pure tests и peer review PASS; direct children+own tare без двойного счёта, observed/expected/UNKNOWN, UTC/DST/версии. Producer proof не проверен, QC=false, API/native archive отсутствуют. [[../concepts/retailcase_hu_mass_projection_20261015]].
- Root quality gate1089files/0cycles/debt72,24 architecture/tooling и оба TypeScript PASS. После новых изменений финальный gate повторяется. Последующие23 focused CLOSE checks PASS, включая malformed saved envelope без нового исполнения.
- TEST EMPTY через прежние pinned OPC сертификаты/7NodeIDs, native claim/zero/raw binding PASS. Первоначальное нулевое наблюдение оказалось раньше claim; native правильно отказал, producer ждёт реального timestamp в claim, исходные данные не переписываются. Новые попытки B/C имели отдельные request IDs после подтверждённого терминального состояния.
- [[../components/retailcase_joint_sql_review_20261015]]: bounded аудит и конкретные решения; не объявлять cumulative V$SQL сценарием/p95 и не выдавать прямые native вызовы за HTTP.

## Следующая очередь и ограничения

Магазин: GS1-128 исправлен exact-first fallback в выбранном магазине и привязкой
только к текущему preview. Старые frozen intents не изменяются.20 focused checks,
реальная программная камера с байтовым повтором и 5 live GET вариантов PASS.
Последний полный gate1095/0/debt72+24tooling+обаTS PASS; terminal production build PASS.
SQL7 Oracle/local pairs, maxHTTP408ms/own slow0; новый индекс/кэш не обоснован.
[[../components/retailcase_operator_ui_evidence_20261015]].
Store API ошибки не показывают технические пути, status/code остаются в объекте;
13 request/message проверок и финальный повтор gate/build PASS. SHIPPING_GROSS
placement claim bound подтверждён VALID UNIQUE по CASE/UID; thermal assert_cell
прочитан отдельно. Metadata constraint query3469ms имеет решение и владельца,
полная transitive purity и ранняя граница compiler work остаются открытыми.
Кандидат README и SHA-манифест согласованы, прежний manifest сохранён; SQL bytes
не менялись. Live production shift UI390 PASS (11 HTTP200/overflow0/qty0),
первый teardown-failed прогон явно не принят. Полный live набор4ресурсов пока
отсутствует. Новый существенный остаток: recovery-shorts не принимает actor/ware,
нужны native scope и фильтр доlimit перед использованием как обзора одного WARE.
SQL desk first1469ms/second823ms, три slow entries имеют module owners и backlog
в [[../components/retailcase_joint_sql_review_20261015]]. Следующее поручение
Claude подготовлено в [C0115](../../coordination/retailcase-claude/PROMPT_CLAUDE_C0115_CHECKPOINT.txt),
но новый ACK не получен и работа реального Claude не заявляется.

Точное начало следующего recovery инкремента: `main.py:120` сейчас связывает
`recovery_view` с flat `case_pick_view`; `recovery_routes.RecoveryPort.list_recovery`
принимает толькоlimit. `recovery_tasks.py` уже join-ит RRL_PICK_WAVE w, но не
фильтрует его склад. Потребителей2: `shift/useShiftData.ts` и `TwinDesk.tsx`.
Добавить actor/ware через публичную границу, current native `case_pick_view`
проверять по фактическому складу до чтения/limit, READ ONLY и bind variables.
Оба потребителя должны передавать выбранный склад и отбрасывать старый ответ.
Совместимость запроса безware определить явно через текущие допустимые области,
а не оставить альтернативный глобальный bypass. Соседний `list_inventory` тоже
legacy read; его область — отдельный проверяемый пункт, не молчаливое расширение.

Текущие11 source/test SHA и результаты root команд сохранены в
[GS1 final manifest](../../reports/retailcase/2026-10-15/store-camera-formats/gs1128/final-source-manifest.json).
Это локальные fingerprints и наблюдённые проверки, не независимая аппаратная
приёмка. В API оставлен root `serv.bat` на8088, процесс41348; новых SKU/остатков/
товарных команд в заключительных GS1/shift проверках не создавалось.

1. Независимый live readback положительного CASE и postpositive retirement завершены: actor deleted/resource63 inactive/qualification0/rolev4inactive, session59CLOSED,24/H0/clockv8OFF, INVALID0; все истории сохранены. Старый empty cleanup не запускать.
2. HU mass transparency UI завершён:14new+17existing model/3rendered и actual native read390 PASS. HU read scopes WARE/GROUP/current revoke actual HTTP PASS, фикстура N2140 retired. [[../components/retailcase_hu_scoped_read_20261015]]. Shipping-domain native read подготовлен как кандидат, SQL не применён, независимый review ещё требуется. SHIPPING_GROSS request/claim/capture/use/loading не реализованы.
3. AK06-F: mixed ASM/rack tree сквозь физическую консолидацию, совместимость температур, CASE-preserving interWARE bridge и scoped subtree handover магазину остаются открытыми.
4. KPI: оба знаменателя владелец принял. Числители, rule attribution строки и физическое delivery event пока не утверждены; pending async вопросы не являются согласием. Manual WORK не объявлять полной фактической активностью.
5. Физические весы/сканер/телефон и commissioning, нагрузка/пилот/legacy cutover отдельно. Реальный Claude Code временно ограничен provider quota до23:00; продолжение делают внутренние Codex-агенты, не приписывать их работу Claude.
6. Google Drive upload ранее заблокирован автоматической проверкой из-за неподтверждённых аккаунта/папки. Ссылки на загруженный документ нет, блокировку не обходить.

API8088 запущен root `serv.bat` без reload; секреты QA в ignored runtime, никогда не печатать. Pinned TEST OPC server ограничен30мин и может завершиться; повторять только прежний профиль, не выпускать новые сертификаты ради теста. Oracle DDL только root, fresh source/manifest/readback/INVALID guards, no blind reapply. Не запускать старый cleanup1139 с предположением picked0/parent23.

После замечания о расходе: лишние параллельные ветки остановлены. Последний полный gate1094/0/debt72+24tooling+обаTS PASS; повторять только после нового функционального изменения, не ради отчёта. [[../components/retailcase_development_cost_skills_20261015]].

Следующий read-кандидат root просмотрен частично: locking `assert_allowed` заменён на pure allowed+NULL denial; dirty borrowed TX отклоняется до собственного rollback.15 focused doubles и один повторный полный gate после Python-изменения PASS. Исходный кандидат сохранён до исправления; SQL не установлен, полный native review/kit/acceptance остаётся впереди. Это одна текущая ветка, новые агенты не запускаются.
