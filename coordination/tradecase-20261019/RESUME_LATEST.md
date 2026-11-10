# RESUME — 2026-10-27 22:30 Europe/Moscow

## 2026-10-28 08:47 — C0192 review and C0190 transport remainder

- Last read Claude message: K-0224, C0192 RELEASE. C0192 is received, not accepted. K-0225 requested a same-request rework; ACK is pending. Do not describe Claude as working until that ACK arrives.
- Root changed only C0190 files. Cleanup uses the persisted C0191 expected_remainder_after_load; it validates the two owned articles and refuses an invalid value. It also refuses to run after C0192 declares warehouse finalization. Tests: C0190 79 PASS; RETAILCASE quality gate architecture/tooling 24 PASS; encoding PASS.
- C0192 defect: retire() directly updates RUSERS/RIGHTS without a durable journal command or reconciliation. The required rework stops before retirement until a durable owner finalizer exists, preserves prior safe stages, and proves no user/right SQL is sent.
- C0191 remains owned by Claude for the already queued DOCID/recovery rework after C0192. The partial ST 643010 has no rows or fulfillment records; do not alter it. No API restart, live Oracle write, hardware call, or GitHub publication occurred in this checkpoint.

## 2026-10-28 09:00 — C0191/C0192 channel status

- C0192 rework K-0227 is accepted at commit 7e1455d7 only through the durable stop before retirement. It leaves synthetic users and rights in place deliberately; no direct DML is allowed until a root-owned journaled finalizer exists.
- C0191 K-0230 was reviewed and not accepted. The bounded 15-character DOCID repair and metadata recovery tests pass, but stored shipment metadata needs the complete immutable command descriptor and fulfillment reconciliation must validate every owned field. Rework 2 is in TASK_C0191_REWORK_2.md and K-0231. ACK is pending; do not call Claude active until it arrives.

## 2026-10-28 09:12 — owner finalizer and C0191 ACK

- Root added Live.finalizer_sql to C0190. It saves the SQL command and verification query before execution, distinguishes a first pre-existing result from resume reconciliation, and preserves unknown outcome after a failed write until exact verification succeeds. The focused C0190 suite is 80 PASS.
- K-0232 ACK received for C0191 rework 2. Claude owns only C0191 source/tests/report and will save immutable metadata descriptors, validate complete fulfillment rows, and test changed intent. This is ACK, not a release.

## 2026-10-28 09:20 — accepted C0191 recovery; C0192 finalizer queued

- C0191 rework 2 K-0233 was accepted at commit 0909a0d0 after root reran 43 focused tests. SHIPMENT now stores an immutable descriptor before each metadata write, refuses a changed descriptor, and reconciles only fully matching fulfillment rows.
- C0192 finalizer follow-up is in TASK_C0192_FINALIZER.md and K-0234. TASK.md now points to it. ACK is pending. It must use root-owned Live.finalizer_sql and not mutate C0190/C0191. No live mutation, restart, hardware call, or publication has occurred.

## 2026-10-27 23:27 Europe/Moscow — C0187 reviewed

- C0187/K-0209 delivered a focused offline test file for weighed-line and weighted-box CASE write paths. Commit `351040ee`; no production code changed. Codex reran the scoped suite: 36 passed; RETAILCASE quality gate PASS; encoding and architecture PASS. No Oracle writes or API restart.
- Source review confirms that `/api/warehouse-hus/attach-case` accepts a CASE child and `/attach` accepts a child HU; native HU attachment checks same warehouse/cell, versions, parent container, cycle, parent ownership and 200-node bound. This establishes available composition primitives, not the requested live mixed tree.
- T06 stays partial: no end-to-end accepted parent containing both a weighed CASE child and shelf-picked box/each child. Physical scale commissioning and full external role/ACK matrix also remain open.

## Instruction and constraints
Owner instructed Codex to continue TRADECASE/BLC work until all feasible sprint work is complete or midnight Moscow. T01 done; T02–T12 remain partial. Do not publish to GitHub without a new direct instruction; never publish SAP/SAP_INTEGRATION. User wants compact, evidence-based work and routine decisions made without small clarification questions. Keep wiki/index/log and sprint checklist current. Oracle changes require source, frozen manifest, explicit project authorization, safe target, live apply/verify and rollback constraints. RETAILCASE changes require the modular contract/policy and quality gate.

## Accepted since the prior checkpoint
- **C0183 T10** accepted K-0202: four confirmed yard refusal messages, focused test 9/9, TypeScript, quality gate, encoding and architecture pass. No live writes.
- **C0184 T10** accepted K-0204: 22 GETs on API 8093, all 200, payload/event/assignment IDs matched, no SQL rows attributable in slow log. One of two ×4 concurrent rounds per warehouse sometimes reached about 1 s; cause unproven. Backlog for API owner: record pool acquire time and open connection count; no speculative code or index change.
- **C0176 selected-place removal**: migration ledger shows APPLIED in RABAEV@orcl at 2026-10-27 04:04:26. Source hashes match after manifest; changed packages VALID, INVALID=0 and USER_ERRORS=0. Live test on own warehouse 241232574 passed: remove 2/4, exact replay, changed body and stale snapshot refusals, competing requests 200/409, identical concurrent retry 2×200 with one receipt, unauthorized actor 403. Focused pytest 7/7; both endpoints present in served API 8088; earlier UI 1440/390/lost-response test 7/7. No stock changed. Cleanup left zero pallet rows and inactive access, but retained the inactive QA warehouse and 3 audit rows intentionally. Do not delete history. Evidence: `runtime/test-evidence/tradecase/2026-10-27/C0176/PR27afc0154d5e.json`.

## Claude
C0184 released K-0204. C0185 accepted K-0206; C0186 accepted K-0208. C0187 delivered and was reviewed (K-0209, commit 351040ee); Codex reran 36 focused tests and the RETAILCASE quality gate. Source review confirms CASE/HU attach primitives but no live mixed weighted/shelf tree acceptance. C0186 remains committed locally as 7e8fcb47; no GitHub push.

## Codex performance work
Current local changes: `resource_timeline.py`, `timeline_queries.py`, `timeline_projection.py`, `tests/retailcase/test_resource_timeline.py`. Visible-event bindings reduced response assignments 1281→1 for one live six-hour set without changing event/assignment identity. Admin fast path calculates `RRL_ACCESS_API.is_admin` once; same set median direct service 3217→2811 ms. Focused tests 24 and RETAILCASE quality gate pass. `loading_rows` remains about 1.5 s; nonadmin timing cannot be measured because no eligible account/data pair was found. No index added; actual plan stats unavailable without DBA access.

## Remaining work
T02–T12 remain partial. Open constraints include SAP/СКМ external transport and business ACK, T03 DESADV/negative set, T04 full wave concurrency, T05 reverse ownership/financial accounting, T06 mixed BOX/weighting/role matrix, T07 concurrency and external documents, T08 authoritative pallet-place/stacking profiles plus proposal competition/rights, T09 external route/window data, T10 full resource competition/load (C0185 closes the live blocked-dock refusal; four other warehouses have REACHTRUCK lanes and warehouse 213059748 has an existing QA PICKING_MOVE shown/selectable in the real UI; OTHER is unregistered), T11 supplier returns/equipment/physical paper workflow, T12 full 45-case acceptance/pilot. Positive top-up remains fail-closed until the recipient pallet/stacking profile is authoritative. SAP/СКМ PENDING is not delivery.

## Runtime
API 8088 PID 87992 and API 8093 PID 24236 were left running. Do not restart either without coordination. C0184 made GET-only calls and left processes unchanged. Stop by 24:00 Europe/Moscow if any sprint work remains.
---
# Archived prior resume history

## C0175 применён, C0176 в работе

Root применил units-kit после91908992:6/8/6, INVALID0/USER_ERRORS0, after-kit ASGI+Oracle223057509 PASS. Root поправил mixed-line receipt, persisted-winner readback, точный Fraction, целый шаг нынешнегоEA/BOX и WAITING loaded=false;15адресныхтестов PASS. Профиль200строкодногоSKU:401SQL/1887мс →3SQL/34мс READONLY при полном равенстве. Кэш только внутри заказа. Новый общий8088 ещё не перезапущен, ждём C0176 native/RELEASE для одного restart.

C0176 ACK+CONTRACT K0179 BUSY: Claude owns transport/native selected places/UI. Root замечания в конце CODEX_TO_CLAUDE.md: hash snapshot вместо count, strict IDs, unknown outcome403/conflict, replay lookup послеTTlock, bounded1000/nullware/access-lock. Не применять незамороженный комплект до RELEASE.

Root подготовил reduce() в tests/tradecase/live_program_orders.py и изменил load(): только после REDUCED_READY, исключает20retainedkeys, ожидает640LOAD/64m3, остаток4600/H200/460. Пока не запускалось. Набор210069361 всё ещё TRANSPORT_READY/33698/11000H6600. ПослеC0176apply/restart: reduce, load, документы/выезд640, коды/остаток20/исходящие. Не выполнятьстарыйload660/DEPART660.

Новый документ и ZIP NICORA опубликованы и проверены; ссылки ниже. НативныйGoogleDoc211полей/24таблицы, архив25CSV (23входных+словарь+ожидаемыйрезультат). GitHub не публиковать без нового поручения.

## Последняя задача владельца: приложение NICORA опубликовано

Отдельный Google Документ со словарём211полей и примерами: https://docs.google.com/document/d/1wftqBkWDad207yB1iXTbtLW5FeApc1aq4--K3N1x8QA . ZIP 25 CSV / паспорт / manifest: https://drive.google.com/file/d/1Fo0cWh8gvNT44rhirYl_xR6MBpX7D0F9/view . Оба рядом в ChatGPT, metadata/readback подтверждены. 940ячеек сверены, локальные SHA/ZIP/ссылки/дерево/месяц проверены; PDF в runtime/nicora-export-fields-review.pdf, таблицы с повтором заголовка и без разрыва строки. Локальные файлы docs/integrations/nicora/, wiki/requirements/nicora_export_fields_examples_20261027.md. Это синтетический профиль CSV, не выдуманный IDoc и не приёмка SAP. Публикации GitHub нет.

Владелец поручил продолжать все спринты совместно с Claude. C0175 зарегистрирован до передачи, бюджет37/37, K0177 ACK+CONTRACT подтверждает BUSY. Claude делает новые единицы заказов, owns contracts_tradecase.py, tradecase_documents.py, order_units.py и NOT_APPLIED native тела RRL_TRADE_ORDER_API/RRL_TRADE_DOCUMENT_API. Root согласовал контракт в конце CODEX_TO_CLAUDE.md. Не менять эти файлы параллельно. Live baseKG в TRADECASE и NI02 остаются открытыми; чистые тесты дробности не выдать за их реализацию. Claude не перезапускает API и не трогает root210069361.

Root возвращается к640/20: все660мест уже назначены33698;60мест добивки в одномST. Проверить решение частичного снятия фактических мест через существующий единый writer; не делать прямойSQL-обход и не переименовыватьST ради теста. Состав после частичного снятия может сохранять номерST; требуется проверить текущие ограничения и права/идемпотентность. DEPART660 запрещён. Ниже состояние транспорта остаётся актуальным до новой стадии.

## Актуальное продолжение 27.10 после назначения рейса

Рабочий набор 210069361, state.resumed.json: TRANSPORT_READY. Все 660 коробов отобраны и назначены рейсу 33698 четырьмя СТ 200/150/250/60. Остаток 11000/H6600/1100. grouped-st-assignment применён/откачен/повторно применён 9/9/9 после ae1d2a8c, INVALID0. Первый запрос после компиляции дал ORA-04068/503; readback доказал отсутствие частичного эффекта, повтор исходного запроса прошёл. Доказательство reports/tradecase/2026-10-27/codex/grouped-st-assignment.json.

C0174 RELEASE 5a2c1d58: исправление принято через HTTP после безопасного перезапуска. API serv.bat reload0, PID32476, session38847; DSN127.0.0.1:1521/orcl. Малый рейс 226192056 показывает 0,8/0,8 м³. Claude IDLE; новых заданий нет, бюджет36/36. Основной прогон тестов342PASS +1ошибка TEMP; все5тестов аудита повторены с workspace basetemp и прошли. Gate/encoding PASS.

Следующее: исходные60мест добивки объединены одним СТ. Проверенные API снимают/переносят целый СТ, поэтому требуется штатное выделение20мест, затем TRIP64м³/40BOX добивки, LOAD640/остаток20, выезд, события. Не исправлять ST_NUMBER прямым SQL ради теста. DEPART660 не выполнять. Активного производителя физического прогона сейчас нет; не запускать load660 без этого решения. T08 и остальные частичные спринты не завершены. Google Doc NICORA: https://docs.google.com/document/d/1jQDT6Q75OkmHUIp0NyBweIoc7L8bVUEavR-LiZQ5knI . GitHub не публиковался.

Ниже история; она не заменяет этот блок.

## Последнее состояние 27.10 — отбор завершён

Набор 210069361: PICKED, все 660 коробов собраны; использовать только state.resumed.json. C0173 применён/откачен/повторно применён 7/8/7, INVALID0. Перемещение 4109 выполнено один раз, повтор проверен. Transport stage создал собственный рейс; назначение остановилось на границе 200 мест одной сборки. Миграция db/migrations/2026-10-27_grouped_st_assignment применена после ae1d2a8c, откат/повтор прошли 9/9/9. Продолжить сохранённый transport.assign без нового рейса, сначала проверить состав после прежнего отказа.

Claude C0174 RELEASE: RESULT_C0174.md, коммит 5a2c1d58. Малый сценарий 6+3→8/1 проверен. trade_topup.py исправляет фиктивный учёт ADOPTED остатка; на API появится после безопасного перезапуска. Все 60 мест нашей добивки входят в один СТ; требуется проверить штатное выделение 20 мест. SQL-обход назначения запрещён. DEPART660 не выполнять. Ниже сохранена история; она не заменяет этот блок.

## Активная работа27.10

Владелец возобновил Claude. C0172(обращение34) подтверждён K0168; реальный полный маршрут OSRM/окна/перерыв120/15 проверен автором, root вернул UI/тесты на исправление. Claude занят REVIEW: пояс исходных значений, ExtraStop, переносимые fixtures и UI. После RELEASE назначен C0173(обращение35): существующий путь660→640/остаток20 и проверка учёта adoption. TASK и журналы coordination/retailcase-claude действуют; резерв чужих файлов соблюдать. Не считать очередь новым завершённым результатом.

Root выполняет tests/tradecase/live_program_orders.py на складе210069361. Приёмка1100BOX завершена; основные3заказа600BOX/6000EA, добивка60из80 и adoption600EA теми же RID/units прошли через8088. Стадия PICKING остановлена после350BOX на операции TP26.010ef1ba.move.4109 с TRADE_ORDER_BINDING_STALE: настройка добивки/X поменяла C103v1→v4, прочие поля не изменились. Процесс84372/exec87537 завершился с отказом, не работает; лог runtime/test-evidence/tradecase/2026-10-27/T08/program-orders/pick-http-stage4.txt. Товар11000/H6600/1100сохранён. Claude готовит C0173: минимальная совместимость разных версий только при равенстве payload без двух полей добивки, helper+RRL_TRADE_PICK_CONTEXT BODY+RRL_TRADE_TRANSPORT_CORE BODY; root дал резервы, сам не правит. Ждать RESULT/RELEASE, проверить/checkpoint/apply/rollback/reapply, потом продолжать pick. Не переписывать LINK/версии вручную. Проверить исход неуспешной операции перед выбором идентификатора повтора.

Главный state — state.resumed.json: старый state.json перестал заменяться Windows, сохранены оба исходных файла/checkpoint и точный putaway.1077. Default runner выбирает recovered state и блокирует возврат к старому. После pick: stages transport, затем load; подготовлены, ещё не прогнаны. Никакого DEPART660 до проверки исходного640и остатка20. Общий API черезserv.bat, reload0, PID94460, Oracle127.0.0.1:1521/orcl; не перезапускать при работающих командах. Интегрированный build exit0/336tests/gate прошли. forecast_ui_check.cjs дал реальные GET1440/390 без бизнес-записей; картинки прочитаны, таблица на телефоне имеет внутреннюю горизонтальную прокрутку, полная матрица UIотказов не заявлена.

Сохранён новый документ wiki/requirements/nicora_sap_stand_data_request_20261027.md и Google Doc https://docs.google.com/document/d/1jQDT6Q75OkmHUIp0NyBweIoc7L8bVUEavR-LiZQ5knI . Текст сверен. Нужны IDoc, магазины, товары/дерево/конечная категория слоттинга, остатки, заказы, дневной прогноз продаж на месяц и отдельный прогноз перемещений. Новые владельческие правила единиц записаны wiki/requirements/nicora_order_units_20261027.md: шт/короб/блок/г/кг по SKU; при единственной единице обработки округлять вниз в обоих режимах, при выключенном разрешении строку всё равно загружать и сохранять ошибку интеграции. Не отклонять строку по этому признаку. Реализация этого расширения ещё не сделана; текущий TradeOrderLine EA/BOX и baseEA ограничены. Исходные количества не переписывать.

Миграции27.10 source-window/forecast-guard/cancelled-trip-assignment применены7/7/7 с checkpoint62e1d469/3d14cd7c/5a566ed2, отдельный ASGI/Oracle набор CLOSED39вызовов/H0/INVALID0.331TRADECASE tests и quality gate PASS до изменений C0172. Zero-capacity TCP proof:852/190/194мс, запас11000/H6600/1100до/после, предложение0 и stock=null; решение без нового индекса/кэша. Inner READONLY1901→14мс не выдавать за HTTP/SLA. Последующие проверки — после RELEASE Claude и завершения собственных стадий. GitHub не публиковался; SAP/SAP_INTEGRATION исключены. T01готов, T02–T12частичны; DONEcomplete не создавать.

Ниже сохранена история прежних результатов; устаревший STOP Claude и подготовленные статусы не заменяют этот блок.

## Текущий результат

Локальный масштаб660мест ЗАКРЫТ: склад225290508, план2285, волна636DONE, рейс33687DEPARTED,660отправокSHIPPED/6600EA,660складскихзаданийDONE, остаток0/H0. ПользовательTC03e9508cd7отключён, назначенияотозваны. Наборphysical/state.json=CLOSED/PASS_SCALE_ONLY. НЕ переоткрывать и не менять phaseдляповтора. Все5проверенныхпрежнихнаборовсохранили0/0или20/0.

ТочныйповторDEPARTдалпрежнийрезультат. ПослеDONE повтореныисходныеrelease иfinish: равнысохранённымответам, волнанеоткрылась,0/H0.660LOADсобытийсуммарно-6600;DEPARTтоварныхсобытий0. Дваисходящихсобытия14420/14421дляSAP/СКМпо6600единиц/кодовравны, PENDING; промышленнойдоставкинет.

Главныйотчёт: wiki/roadmap/tradecase_evening_result_20261026.md. Livingchecklist: wiki/roadmap/tradecase_execution_20261019.md. T01готов;T02–T12частичны. Этотнабор—1SKU/1заказ/1получатель, НЕисходные3заказа/1100BOX/660→640/66→64м³. Веса/габариты/внешниеответысинтетические. Ручнойвеспринятвладельцем; аппаратнуюприёмкуучитыватьотдельно.

## Продолжение 27.10.2026

После отчёта владелец прямо поручил продолжить выполнение. Работа снова разрешена; прежняя остановка в полночь относится к завершённому циклу26.10. Codex работает самостоятельно, без новых обращений Claude. Новый набор: склад210069361, runner tests/tradecase/live_program_orders.py; состояние runtime/test-evidence/tradecase/2026-10-27/T08/program-orders/state.json. Приёмка1100 независимых коробов двух товаров запущена. См. wiki/roadmap/tradecase_program_orders_20261027.md. Этот набор ещё не принят; старый CLOSED не переоткрывать.

## Прежние разрешения и предел26.10

Уточнение владельца27.10во время продолжения: источникдобивки—прогнозпланаперемещений, незаказ. Получатель(магазинилиадрессклада)должениметьвключённоеtopup_enabledигоризонтtopup_horizon_days. БеззагруженногопрогнозаMOVEMENTдобивказапрещена. План:wiki/requirements/tradecase_topup_forecast_20261027.md. Кодконтрактов/чтений/UI изменён;44адресныхтестапрошли. Окнозапаса2026-10-27-topup-source-windowприменено7/7/7после62e1d469. Комплект2026-10-27-topup-recipient-forecastподготовлен, требуетcheckpoint/apply/rollback/reapply/live. Необъявлятьготовым. Приёмка1100мествпроцессе90140;неперезапускатьпараллельновторойэкземплярrunner. APIreload0, новаяPythonлогикаещёневыкачена:перезапуститьserv.batмеждубизнесэтапами.

Поручение26.10действовалодополуночи27.10МСК; циклостановленвовремя. Продолжениеразрешеноновымпоручением27.10выше. Claudeнедоступендо29.10; новыхобращений0, общийсчётчик33. GitHubнепубликоватьбезновогопрямогопоручения, SAP/SAP_INTEGRATIONисключены. Не создаватьDONEcomplete приоткрытыхспринтах.

## Следующая работа

1. Исходные3заказа/1100BOX, основные600+отдельнаядобивка60/80; новыйизолированныйнабор, не этотзакрытый.
2. Замена66→64м³, добивка60→40, адресныйостаток20, приоритетосновныхзаказов, конкуренциядвухпредложений. Не заменятькороба33паллетами.
3. Полныемаршрут/окна/ресурснаяматрица, возвраты/бумага/тара, фактическиевнешниеформатыиответыSAP/СКМ/L4, пик/пилот.
4. Ускоритьnativeчтенияконтекста/исполнениябольшойволныпоравнымснимкам; неослаблятьколичества/ACL/подписи/идемпотентность.

Источникпрограммы—сохранённаяrevision27вwiki-raw/tradecase_source_review_20261021/program.txt; свежаяпроверкаDrive26.10непроводилась. СНС/BLC—TRADECASE, неRETAILCASE. Норма120минвождения/15отдыхаиэталон12:55/14:10сохраняются.

## Среда

OracleRABAEV@127.0.0.1:1521/orcl, INVALID0. ЯвноустанавливатьWMS_ORACLE_DSN иload_local_oracle_environment. API8088rootservsession34626/PID83872,reload0; логruntime/test-evidence/tradecase/2026-10-26/api-route-places-start.txt. Front3000пересобранпослеподписейцелыхгрузовыхмест, buildPASS. ОтдельныйMINIMAXworker39176/склад1/30составленработать, кэтомунаборунеотносится.

ОбычныйUOW30с, WAVE_LAUNCH/WAVE_PICK_RELEASE90ссединымdeadlineнаповторы, попыткаблокировок6с. DEPART/FINISH660прошлив30с:11,32/11,32с. Не подниматьбюджетывсехкоманд.

## Применённые комплекты и SHA

Всеdb/migrations/2026-10-26_* комплектысcheckpoint/apply/пустойrollback/reapply. Не редактироватьприменённыеисточники.

- carton_trip_bounds12/12/12; carton_load_admission8/8/8; pick_plan_sources8/8/8; wave_place_bounds11/11/11.
- carton_lock_budget8/8/8с8спопыткойНЕрешилсбой; заменёнexisting_unit_guards8/8/8с6с. LOCK_API8024DEB8…; существующиеUNITдержатсяrowlockNOWAIT, новыеUNITивсеостальныемьютексысохранены. Прототипыконкуренциистарый/новый/новый, удалениеguard, STOCKкачествапрошли; независимогоревьюнет.
- stock_verify_snapshot11/10/11: INVARIANT_CORE FDBD5747…, индексRRL_UNIT_CELL_GUARD_IX(CURRENT_CELL,STOCK_STATUS,PHYSICAL_UNIT_KEY,CURRENT_UID). RootPOSTING_API EB977210…неизменён.
- box_load_class12/11/12: добавленBOX, TYPE_API71383280…неизменён. ОткатсиспользуемымBOXбезопасноотказалсядоDDL; тип35сохранён.
- route_assignment_places10/10/10после72b17ad1: PLAN_API6CDFAAD7…/RULESC78D40A6…,1000общихстрок,200выбранныхСТвпачке. Перваяпопытка94842649остановиласьдопакетовиз-заошибочногоpreflight, журналысохранены; успехsuffixv2.
- wave_snapshot_items9/9/9после2dde2fe9: FINISH_CMD28B28B7E…, общийснимок5000,1000отборов. Реальный1320снимокифинальныйPOSTпрошли. Ошибочныйrefresh-syncURLвподготовщикеисправленнадействующийfinish-execution.

## Проверки и доказательства

runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/:
- physical/report-final.json иstate.json: CLOSED,9953зафиксированныхвызова, последующиеreplayотдельно.
- final-owned-events.json:4APPLIEDкомандыпо1,2PENDINGсобытия,0повторныхрасходов,QAretired,5прежнихнаборов/INVALID0.
- physical/replay-after-close.json: release495мс/finish209мс, ответыравны,DONEсохранён.
- physical/loading-ui-LOADED660.json/PNG:1440/390,660/660,2,08/1,79с,tooltip/help/последняястрока/модель403. Настоящий403—physical/actual-loading-rights.json. Не выдаватьмодельзаотзывправ.
- physical/shift-660-closed-ui.json/PNG: завершённаяволна,0открытыхзадач. physical/box-type-ui.json/PNG:BOX/44px/подсказки/help,unknown422.
- route-points-660.json:10SQL/660точек272мс,HTTP465мс,результатыравны.
- final-acceptance-quality.txt:PASS,24теста,обеTS. Финальныйencoding/diffпроверитьпоследоков. Baselineнеувеличен.

NativeUOWнепишетотдельныеSQLвslowlog; использованыDBMS_PROFILERrun21–23. RRL_SQL_SLOW_LOG/adminendpoint/topSQL/localHTTPпрочитаны. V$SQL_PLANнедоступен.40ячеек421→176мс, неSLA. Снимокдопуска660~2737мс, исполнения~4,8с; нужныбатчиконтекста/связей. ОчередьCASE/таймлайнтакжевbacklogCodex;транзакционные4–5сметкиневыдаватьзавремяодногоSQL. ИндексHARDIDснакопительными~12мсотложендоизолированногосравнения. Приёмка/LOAD660измеренычерезHTTP, полнаядлительностьfixtureвключаетбольшиеcheckpointфайлы.

## Файлы и история

Веткаfeature/transport-dispatch-phase1. Последниенативныеcheckpoints23584714/0f14660f/72b17ad1/2dde2fe9, UIc162e6c0. Финальныетексты/подписи/этотконтекстсохраняютсялокальнымкоммитом; удалённыедействиянеразрешены.

Чужиеизменениянеприсваивать: CLAUDE_STATUS.md,CLAUDE_TO_CODEX.md,RESULT_C0170/RESULT_C0171,probe.cjs,probe.tmp. Кладовщицкий/терминальныйlegacyдоступиGLOBAL_ADMINсемантикасохранены. Всеоперацииснеизвестнымисходомповторятьс прежнимoperation_id/телом.

[Полнаяпредыдущаяхроника](history/RESUME_before_20261026_2356.md). ИсторическийSTOPPED_20261026.jsonотноситсяк19:00, нектекущемурезультату.
## 27.10 — запрос данных NICORA

Подготовлен wiki/requirements/nicora_sap_stand_data_request_20261027.md. Google Документ: https://docs.google.com/document/d/1jQDT6Q75OkmHUIp0NyBweIoc7L8bVUEavR-LiZQ5knI . Текст и заголовки сверены чтением. Добавлено уточнение владельца: дерево каталога, конечная категория товара и параметры категоризации для предложения автоматического слоттинга. Это запрос данных, а не готовый новый адаптер; реальные XML NICORA ещё нужны. GitHub не публиковался.

Фоновую приёмку program-orders не перезапускать: при проверке state сохранял phase=null и 6470 шагов. Старое поле error не доказывает новый отказ; проверять процесс и последние шаги. Сессия приёмки 90140, окончательная проверка тестов/quality gate 20716. После документа вернуться к T08, сохранив ограничения и checkpoint из истории; не объявлять спринты завершёнными.


## 27.10.2026 23:15 Europe/Moscow — latest

- C0185 is complete and RELEASE K-0206 is accepted. Real UI/API test against 8093 at 1440/390 attempted a plan on blocked dock B22D1161 and received 409 `YARD_DOCK_BLOCKED`; the C0182 text appeared, no plan was created, dock was reopened, owned visit 638 cancelled, and stock/other visits/plans were unchanged. Tagged SUPPLY metadata remains by design; no API restart or code change. See `coordination/retailcase-claude/RESULT_C0185.md`.
- T10 checklist now records the live gate as verified. T10 remains partial due to full resource/shift concurrency, wider resource types, and load coverage. T01 is the only fully closed sprint; T02–T12 remain partial. External SAP/СКМ, equipment and pilot evidence remain open.
- Fixed the stale `shift_gantt_rendered_mock.cjs` assertions: stage SVGs are groups, and the three open CASE states place the wave in PICK despite incomplete preparation. The offline mock passed at 360/390/1440; no production code changed.
- C0186 accepted on K-0208: shared help hint is clamped to the viewport and flips below the button near the top edge. Claude's saved live run covers hover/focus/Escape at 320/390/768/1440; quality gate, TypeScript, encoding and architecture passed. The root's extra full-script rerun could not find the dock-block control in its fresh 320 px session after the plan-refresh assertion; the saved C0186 run and 390 px screenshot do show it. This is a data/UI-path reproducibility caveat, not evidence of a tooltip failure.
- T10 read-only API/UI check confirms one REACHTRUCK lane on each of four other warehouses at 390/1440 (8 screen runs, no POSTs, no page overflow). The 6-hour sample was empty, but a 7-day window at warehouse 213059748 returned four events/six assignments, including QA `PICKING_MOVE · 1248` assigned to the reach truck. Real shift UI at 390/1440 showed the bar and opened its detail card; no tasks were created. OTHER remains unregistered. Evidence: `t10_reachtruck_source_check_7d.json` and `t10_reachtruck_work_ui_check.json` under `reports/tradecase/2026-10-27/codex/`.
- Full offline `pytest tests/tradecase` passed 394 tests. Initial default run failed during `tmp_path` setup because Windows denied scanning shared `%TEMP%\pytest-of-roma`; repeat with `-p no:cacheprovider --basetemp tmp/<unique>` passed. This resolves test execution only, not the live 45-case acceptance or pilot.
C0184 released K-0204. C0185 accepted K-0206; C0186 accepted K-0208. C0187 delivered and was reviewed (K-0209, commit 351040ee); Codex reran 36 focused tests and the RETAILCASE quality gate. Source review confirms CASE/HU attach primitives but no live mixed weighted/shelf tree acceptance. C0186 remains committed locally as 7e8fcb47; no GitHub push.
- Existing offline scale coverage (assembly/warehouse API, gateways, OPC protocol/client) passed 150 tests with 2 skips across 10 focused files; no equipment was connected. This is regression evidence only and does not close the mixed-tree or hardware acceptance.
- C0186 has been registered in the budget and assigned in the file channel for the reproducible 390px HelpButton tooltip clipping. ACK is pending; do not call Claude BUSY before ACK. It owns only the shared HelpButton component/CSS and isolated test; no shared dist, API, Oracle, yard code, or Codex files.
- Root continues independently. No GitHub push; SAP/SAP_INTEGRATION remain excluded.
`tests/tradecase` + `tests/retailcase/test_weighted_case_pick.py`: 430 passed; `node tests/retailcase/hu_tree_model_test.cjs`: 17 PASS. Все тесты offline/pure model, ни одной живой записи в рамках этого прогона.
T06 detail: current `POST /api/case-pick/tasks/{task}/lines/{line}/weigh-line` requires `warehouse_scale_capture`; no proven operator-entered NET path exists for a weighed CASE line. Existing warehouse manual input is empty-case tare/final QC, not quantity confirmation. Existing `T07/bulk-packing.json` proves one pallet with 2 BOX/2 CASE/4 EA of the same SKU only. Preserve this distinction; do not treat it as weighted + shelf-picked mixed-tree acceptance.
Claude returned K-0210: C0187 delivered; no active task, and old C0176/C0174 entries must not be resumed. TASK.md now starts with the current no-task status and preserves prior assignments as history.
24:00 Europe/Moscow: остановка по сроку. Текущая точка и все доказательства — в `STOPPED_20261027_2400.json`; T02–T12 частичны, DONE complete не создавался.

## Continuation 2026-10-28 00:45 Europe/Moscow

- Root independently verified T10 local changes: `tests/retailcase/test_resource_timeline.py` 24 PASS; combined timeline/query/weighted CASE tests 61 PASS; `scripts/retailcase_quality_gate.py` PASS; Gantt browser regression 360/390/1440 PASS; encoding PASS. Evidence: `reports/tradecase/2026-10-28/codex/t10-local-verification.json`. No live SQL run, API restart or Oracle write. Still open: post-restart latency comparison, non-admin owner ACL measurement, full T10 competition/load matrix.
- Claude C0188 delivered local commit `442f80a9`: `POST /api/case-pick/tasks/{task}/lines/{line}/weigh-line-manual`; KG→KG 1:1 admission, server-derived cumulative fact, NET/KG/MANUAL_OPERATOR_ENTRY metadata, canonical same-operation retry/conflict, marking scans retained. Root independently ran 57 focused tests and RETAILCASE quality gate; PASS. No live acceptance and no API restart. This is backend only, not yet available in the operator UI.
- Existing CASE picker UI is mounted from `wiki-raw/wms_admin_ui_reference/case-pick-tsd.html` at `/wms-admin/case-pick-tsd.html`. C0189 registered and delivered through the file channel for UI integration and help; ACK pending. It must use a server-confirmed KG signal and send manual weight only to `/weigh-line-manual`.
- T06 stays partial: live posting/replay on an owned QA line, mixed weighed CASE + shelf BOX/EA tree, store receipt, generic legacy-confirm path provenance gap and hardware acceptance remain open. No DONE.json, no GitHub push. Do not report C0189 active until ACK arrives.
- Claude channel files: `TASK.md` currently points to C0189; C0188 RELEASE K-0212 is in `CLAUDE_TO_CODEX.md`; budget is `coordination/tradecase-20261019/claude-budget.json`.

## Checkpoint 2026-10-28 00:59 Europe/Moscow

- T10 code is local commit `6a9f0101`. Full `tests/tradecase` now passes 396; 61 focused resource-query/timeline/weighted-CASE tests, Gantt mock 360/390/1440, RETAILCASE quality gate, architecture and encoding pass. Offline evidence is at `reports/tradecase/2026-10-28/codex/t10-local-verification.json`. T10 still needs live latency after code reload, a non-admin ACL sample and full resource competition/load.
- T06: C0188 backend route commit `442f80a9`, 57 focused tests and quality gate PASS. C0189 UI is in progress by observed writes at 00:58 to `case-pick-manual-net.js` and `case-pick-posting.js`; CLAUDE_STATUS is stale and still WAITING, so wait for RESULT/RELEASE before claiming it active/complete.
- Root commit `ee5a8718` adds `weighted_kg` to read-only marking policy, true for KG→KG 1:1 and non-serialized weight, including marked KG lines; existing `loose_weight_kg` semantics unchanged. Two policy tests pass and full tradecase count is 396.
- C0189 must wire marked loose-KG lines only with existing required marking scans; serialized weighted boxes stay on their own path. Root owns no C0189 UI files. The generic `/confirm` KG provenance gap and live Oracle posting/mixed tree remain open.
- No API restart, Oracle writes, hardware call or GitHub push. Working tree contains earlier independent pending documentation and coordination edits; don't clean/reset them.

## Checkpoint 2026-10-28 01:14 Europe/Moscow

- C0189 RESULT/RELEASE K-0214 принят. Commit `4723435a` adds manual NET KG CASE flow to the mounted picker and help. Root reran its intercepted Playwright suite: 9 PASS. No real API/Oracle calls were used in that UI run.
- Root fixed carrier move/return error classification: `CURRENT_WARE_FORBIDDEN`, transient errors and operation conflicts preserve unknown outcome; an ordinary native 20882 refusal is confirmed. Commit `be96e8c6`; 35 focused tests PASS.
- Regression evidence: `tests/retailcase` 873 passed, 2 skipped; `tests/tradecase` 396 passed; RETAILCASE quality gate PASS; architecture PASS; encoding PASS; `git diff --check` PASS.
- No API restart, Oracle writes, hardware calls, or GitHub publication. T06 remains partial pending live manual NET post/replay and a mixed tree with weighed CASE plus shelf BOX/EA. Generic legacy KG confirmation provenance remains a gap. T01 only is fully complete; T02–T12 remain partial.
- Local API 8088 is listening, but this checkpoint has not verified that its running process includes these commits. Do not post to it until build/version and owned QA fixture are confirmed.

- C0190 зарегистрирован до передачи в существующий Claude file channel: изолированный fail-closed runner для смешанного дерева KG CASE + shelf BOX/EA. Claude пока не подтвердил ACK; состояние только ASSIGNED/ACK pending. Root владеет Oracle/API исполнением.


- Read-only runtime preflight confirmed that shared API 8088 does not include C0188 manual NET yet; a temporary loopback API on 8095 included it and connected to Oracle (`RABAEV@orcl`). The temporary process was stopped; zero writes. Evidence at `reports/tradecase/2026-10-28/codex/t06-api-route-snapshot.json`. C0190 ACK is still pending; no live posting until controlled QA runner review.

- Read-only Oracle discovery found no currently active assigned CASE task with a non-serialized KG→KG 1:1 line eligible for the manual flow. Live acceptance therefore requires a new isolated QA fixture and cleanup runner; no shared line was mutated.

- C0190 ACK K-0215 reviewed and answered as K-0216. Claude owns the isolated mixed-tree runner/tests only; Codex owns live runtime and Oracle. Decisions: one root SSCC/one recipient, no split store receipt; native uniquely tagged fixture; include root control/load/depart when existing harness permits; manual NET provenance in canonical operation metadata, no DDL. The generic `/confirm` KG provenance gap is separate root work. Claude may edit after K-0216; API/Oracle writes remain with Codex.

- Codex added a source guard for new weighted KG `/confirm` writes: use manual NET or electronic `/weigh-line`; exact replay of an already-saved legacy operation bypasses the new check and keeps native content-conflict protection. Focused suite 36 PASS; full RETAILCASE 876 passed/2 skipped, TRADECASE 396 passed. Query measured read-only 100 times on historical cancelled QA line: median 1.622 ms, p95 3.36 ms, max 9.362 ms; no index. Evidence `reports/tradecase/2026-10-28/codex/t06-weight-source-guard-performance.json`. API round-trip and peak load remain unmeasured.

- The current server function was exercised against Oracle with a unique operation ID on historical cancelled QA line 1077/1081. It returned `CASE_WEIGHT_SOURCE_REQUIRED` before StockPosting; zero writes. This proves the new API service guard with current Oracle config, not active-work or UI acceptance. Evidence is included in `t06-weight-source-guard-performance.json`.

- T06 source-guard code committed as `62108b39`; full RETAILCASE 876 passed/2 skipped includes the added HTTP outcome classification. Claude C0190 runner files were last written around 01:30 after review K-0216; RESULT/RELEASE not yet present.

K-0217 REVIEW: offline runner tests 32 PASS and py_compile PASS. No live run yet. Root found 3 safety blockers: cleanup can count unrelated warehouse stock to zero; native post journal lacks exact body/unknown-result gating; negative attach steps accept any 403/409. Claude to fix owned files and return RESULT/RELEASE; no Oracle writes until then.

C0190 K-0216 result is not accepted for live execution. Codex reopened the same assignment for review rework K-0217 (not a new budget request). Claude must ACK, fix the three concrete safety blockers, run offline tests only, and return RELEASE. No live run has occurred.

## Checkpoint 2026-10-28 02:00 Europe/Moscow

- C0190 RELEASE K-0219 получен. Codex ужесточил native outcome (неизвестный результат по умолчанию остаётся неизвестным) и сделал read-only preflight независимым от операторских измерений. C0190: 60 тестов PASS; RETAILCASE quality gate, architecture и encoding PASS.
- Общий локальный API 8088 штатно перезапущен через serv.bat. /health=ok; OpenAPI содержит marking-policy и manual NET. Read-only Oracle preflight: выбран отсутствующий склад 231693372, ноль остатков/CASE-заданий/волн, коллизий нет, findings=[]. Доказательства: reports/tradecase/2026-10-28/codex/t06-api-ready.json и t06-c0190-readonly-review.md.
- Live run заблокирован кодом FIXTURE_CONFIG_RECOVERY_UNVERIFIED: runner фиксирует справочники раздельными Oracle commit, но не умеет восстанавливать неопределённый исход или очищать частичный fixture. Значения NET/тары не выдумывались. Складских записей не создавали; приёмка магазина и транспорт не подключены.
- T01 завершён; T02–T12 остаются частичными. DONE complete не создан. GitHub не обновлялся.
- Дополнительная защита подтверждена: команда C0190 run без измерений остановилась read-only preflight до записей с тремя отказами: FIXTURE_CONFIG_RECOVERY_UNVERIFIED, PARENT_TARE_KG_REQUIRED, MANUAL_NET_KG_REQUIRED; журнал Oracle пуст. Доказательство: reports/tradecase/2026-10-28/codex/t06-c0190-run-blocked-state.json.

## 28.10 — C0190 recovery

C0190 fixture записывает intent до каждой настройки и сверяет ровно ожидаемую строку при повторе. Новый read-only preflight: warehouse234887495/tag MT287CA085B6C, findings=[], записей нет. Полный run не запускать без значений тары и NET от оператора. После TREE сценарий штатно остановится: LOAD/DEPART/приёмка магазина не реализованы.
## 28.10 — provenance compatibility

Коммиты `36a31fb7` и `5fb5cc3e`: новые электронные CASE пишут источник измерения; старый canonical request повторяется без изменения. Offline backend 57 PASS; intercepted UI C0189 9 PASS. Живых записей нет.
## 28.10 — продолжение по поручению до 06.11.2026

Владелец поручил выполнить предложенные шесть этапов до завершения либо начала 06.11.2026 Europe/Moscow. Тестовые массы допускаются только как явно обозначенные стендовые данные; они не подтверждают физическое взвешивание.

Перепроверка C0190 выявила ошибки предыдущей реализации: лишние bind-параметры в проверочном SELECT; сохранённый HTTP/native отказ возвращался как успешное завершение при повторе; запись состояния могла повредить предыдущий журнал. Исправлены фильтрация параметров, проверка сохранённого статуса и атомарная замена файла после flush/fsync. 67 адресных тестов прошли. Live-записи не выполнялись.

Предыдущие записи о полностью восстанавливаемой fixture считать преждевременными. Принудительный флаг готовности снят. Остались сверка точных значений вместо одного count, восстановление частично созданной волны и команд с меняющимися версиями, затем транспорт/магазин. Существующие preflight JSON сохраняются как исторические результаты, а не доказательство восстановления.
## 28.10 — восстановление T06 и передача C0191

C0190: журнал разрешает пройти завершённые шаги к неизвестной операции; изменение прежнего SQL под тем же ключом сверки отклоняется. Чужая существующая fixture отклоняется и при повторе. Неизвестный исход сохраняется до Oracle-вызова. Идентификаторы заказов и входные данные fixture сохраняются до использования; создание планов/волны восстанавливает найденный документ после потери ответа и не повторяет неидемпотентное создание при отсутствии результата. Команда запуска волны переведена в общий native-журнал. Команда пересчёта тары сохраняет прежние количество и версию; список бронирований не дублируется. Адресная проверка: 74 PASS. Живой mixed-tree не запущен; полная приёмка ещё открыта.

Claude C0191 зарегистрирован и передан через TASK.md и CODEX_TO_CLAUDE.md: отдельный адаптер контроля/погрузки/выезда/приёмки одного корневого места одним получателем. Запрос 1 из 2 текущего выделения, ACK ещё не получен. Основной C0190 runner остаётся у Codex. Следующее действие: восстановление привязки планов/preview и точных версий дерева; затем интеграция C0191. Тестовые массы допустимы только с явным указанием синтетического происхождения.

### 28.10 ? T06 mixed-tree runner, live start and recovery
- C0190 now persists fixture IDs, original command bodies and expected versions before writes; fixture/document recovery and tree restart tests: 77 PASS. Architecture/type gate completed PASS before the latest runner-only changes.
- First live fixture: warehouse 232283592, wave 643. Native launch alone skipped API continuation; release succeeded but no CASE tasks existed. API continuation correctly refused after release. Both plans were cancelled through PICK_PLAN_CANCEL, wave finished through WAVE_EXECUTION_FINISH, own lots cleared through INVENTORY_COUNT; final remains=0, hard=0. No schema changes.
- Runner now launches through /api/picking/waves/{id}/launch, preserving the canonical operation ID. A new isolated run uses runtime/test-evidence/tradecase/2026-10-28/T06/mixed-tree/api-launch.json. Values 20 kg tare and 9.6 kg NET are synthetic software fixture inputs, not physical weighing evidence.
- Claude C0191 was registered/delivered, but no ACK. Direct installed CLI delivery failed before work: OAuth session expired and refresh failed. Continue independently; do not claim Claude is running. Current two-request grant has one registered request; no second task sent.
- Open: complete live KG/EA tree, transport/store receipt adapter, focused SQL review, remaining T02?T12 acceptance. T01 alone remains fully closed.

28.10 correction: K-0220 ACK and K-0221 RELEASE C0191 were missed by Codex. Claude file session is available; CLI OAuth failure does not apply to it. Commit 854e459e restored after backing up Codex draft. Last read K-0222. C0192 cleanup companion delegated (second of current two requests), ACK pending. Root owns C0190/C0191 integration; Claude owns new C0192 files only. Working prompt: coordination/retailcase-claude/CODEX_WORK_PROMPT.md.
## 28.10 — channel checkpoint K-0223/K-0224

- Last read `CLAUDE_TO_CODEX.md` message: K-0223, ACK for C0192. C0192 is in progress through the file channel; no RELEASE yet.
- C0191 K-0221 was restored from commit `854e459e` and its 25 focused tests pass. Root live integration found `RRL_SBORKA_PALLET_ROWS_ADD4` rejects the 16-character generated ST in `DOCID` (max 15). The created root ST `MT28139952A4B.ST.PAL` contains no rows or fulfillments. K-0224 queues a C0191 rework after C0192 RELEASE: bounded/collision-safe DOCID plus durable SHIPMENT recovery. Do not modify Claude-owned C0191 files before its ACK.
- Root retired only its two mistaken pre-integration bindings: CASE 1182/1183 now have no legacy ST binding; their two own fulfillment rows 1598/1599 are `CANCELLED`; immutable CASE event history remains. No stock, reservations, transport load or external message changed.

## 2026-10-28 — channel and mixed-tree recovery

Last Claude message read: K-0238 (ACK C0193). C0193 had ACK only; no RESULT/RELEASE. Owner then limited Claude to UI and strategic work, so K-0240 withdrew its backend block before implementation.

The legacy per-CASE shipment bind rejected the aggregate ST as designed. It had detached KG CASE 1182. Codex reattached it with operation `MT28139952A4B.RESTORE.KG.AFTER.ST.BIND.REFUSAL`; the root `MT28139952A4B.PAL` is again intact with CASE 1182 (9.6 KG) and 1183 (4 EA), root version 4. The aggregate ST 643010 and its rows/PLANNED fulfillments remain unbound. No LOAD, departure, receipt or external acknowledgement occurred.

C0190 `finalizer_sql` now records an unknown journal state if initial read-only reconciliation fails; focused runner tests: 81 passed. Earlier v1/v2 repair records remain `READ_ONLY_REFUSED` before DML. Next root task: implement the native root-HU shipment binding under the inventory module, then connect C0191 to it and complete live acceptance.

C0193: despite K-0240 withdrawal, Claude reported completed code before reading it (K-0242), commit 8be60c93, with no live writes/restart. Root independently ran the C0193 suite: 26 passed; architecture/support portions of quality gate passed. K-0243 accepts the code. The route `POST /api/warehouse-hus/bind-shipment` binds an intact root HU and all child CASEs to one prepared ST in one metadata transaction; it has no live acceptance yet. Claude assignments now restricted to UI or strategy.

Live C0193 acceptance checkpoint: route deployed through `serv.bat`. First exact root-bind call returned HTTP 500 due `RRL_CASE_SHIPMENT_UK` unique `LEGACY_SBORKA_PALLET_ID`; it had no committed change. Migration `2026-10-28_root_hu_shipment_bind/001_allow_many_cases_per_st.sql` was applied and verified. Exact retry of `MT28139952A4B.T.BIND.ROOT` returned 200: CASE 1182 and 1183 both point to ST 643010; fulfillments 1600/1601 are PICKED with their own versions; root still has both cases. Journal unknown cleared only after this exact retry. Next: C0191 transport control/load sequence; no LOAD/depart/store receipt yet.

C0191 continuation: adapter is invoked through `run()` (it has no CLI main). It replays root bind from journal, creates the synthetic dock/vehicle/driver/task/profile, and reaches `FLOOR_QC_TARE`. It stops before QC/tare/load at a confirmed read refusal: `PALLET_FLOOR_CURRENT_SOURCE_REQUIRED` for root `MT28139952A4B.PAL`. No QC, root tare booking, LOAD, DEPART or receipt happened. The adapter was corrected to use root binding on resume, to give `Live.meta` a verification query, and to obey the driver license 30-char API limit; focused tests 44 passed. Next technical work: define/admit the root HU's physical pallet-floor source through the supported inventory contract, then resume C0191.


### 2026-10-28 root tare checkpoint
C0194 strategy accepted. `TARE_BOOK` is the only root-HU type source. Migration `2026-10-28_root_hu_tare_scans` is applied. C0190 now books the root before attaching CASE; C0191 consumes `root_tare_booking`. Focused 129 tests pass. Do not resume `MT28139952A4B` through root tare: its child CASE books predate the corrected order. Create a new isolated fixture/tag for live acceptance.

## 29.10.2026 — новое основное поручение DeepSeek
Актуальная точка входа Codex после перезапуска: coordination/deepseek/CODEX_RESUME.md. Владелец передал оставшуюся разработку DeepSeek через D003; проверять его канал и владение до правок. Прежние записи выше сохраняют историю и не заменяют новое поручение.

