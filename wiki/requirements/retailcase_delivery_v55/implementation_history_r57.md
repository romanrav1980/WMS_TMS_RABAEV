Режим исполнения принят владельцем 14.10.2026: сквозные сценарии с UI; минимум80% усилий на функционал; адресные проверки; отдельные статусы кода, внешней интеграции и пилота; переиспользование WMS/TMS перед новой реализацией. [Правила](../../concepts/retailcase_execution_delivery_rules.md). NI02.2: тип плановой паллеты от адресата подключён1209; фактический тип может переопределяться при сборке. [Результат](../../database/retailcase_ni022_recipient_floor_20261014.md). Следующий стык: показать плановый тип и переопределение в существующем UI сборки; полные спринты этим изменением не закрываются.

# RETAILCASE: план доработок после перехода ядра остатков

**Revision 57, 14 октября 2026 года.** 8 направлений NI01–NI08, **18 функциональных спринтов остаточного объёма**. NI — направление; NI03.1 и аналогичные — текущие спринты без обещанных календарных сроков. 68 NS-карточек/363 сценария редакции 57 сохранены как требования.

Основа: [утверждённый анализ](../../components/retailcase_global_reuse_analysis_20261007.md), [фактический cutover](../../database/retailcase_stock_posting_cutover_20261009.md), [состав JSON](implementation_plan.json). Исходный выпуск commit 320cefb.


## Текущий блок14 октября /1190

Авторасчёт1118/V21148, физическая температура погрузки/выезда1172 и нормативный профиль/общая проверка тары1187 реализованы в dev. Следом — подтверждённый тип физического TOP/HU и deadline сборки/ворота через existing owners. [Отчёт36](../../../reports/retailcase/2026-10-13/36-vehicle-tare-variants-report.md). Предварительная оценка по запросу владельца:80–160часов оставшейся разработки, без срока получения внешних доступов; ещё не измеренный прогноз. Полные спринты автоматически не закрыты.

## Фактическое обновление 12 октября, revision17

Новые изменения используют действующие WMS/TMS и RABAEV. Зафиксированы конкретные рабочие цепочки, полного завершения всех18 спринтов нет. Реализован и адресно подтверждён NI03.1; остальные17 содержат реализованные части и открытый объём.

| Спринт | Последний реализованный результат | Открытый остаток |
|---|---|---|
| NI06.1 | Два плеча многотоварного места: original ST → whole HU receipt → task → existing onward ST/load/depart → buyer3 по каждому SKU; repeated physical loss/recovery сохраняет ключи | Partial/aggregate-only groups, temperature decisions/rerouting, detached loading/high-leaf batching |
| NI04.3 | Локальная отмена исходной коробки/родителей; immutable journal/current-origin scan guard; quantity/codes preserved | Новая юридическая агрегация, остальные scan flows, real adapters/ACK |
| NI06.2 | REFUSED1 → supplier existingST/QC/load/depart; DAMAGED1 → independent disposal; existing custody/receipt/PUT; original buyer3/missing2 unchanged | Aggregate-only/multi-place custody, quality inspection for REUSE, real ERP/Gov decisions |
| NI07.1 | Actual CASE/BOX clocks, dated source partition and one claim; immutable rate revisions; published existing transport tariff norms/current scoped billing sources | Physical mixed-day/source coverage, real financial ERP and independent evidence |

Остальные карточки не снимаются с плана из-за отсутствия новых записей в этой таблице. Их существующие implementedSlices сохраняются. Следующее функциональное действие: NI07.1 — фактическое признание транспортных норм по машинам/точкам/выгрузке на неизменяемых источниках. Ordinary BOX clock и разделение по датам реализованы512–520; физический mixed-day rehearsal остаётся открытым. Затем NI06.1/NI06.2 оставшиеся способы маркировки и custody, NI06.3 тара, NI07.2 закрытие и NI08.1 реальные ограничения.

Данные о стране/режиме водителей, окончательные SAP/XML и государственные сервисы должны подтверждаться реальными конфигурациями. TEST, PENDING, локальный journal и авторские случаи не заменяют внешний ACK или независимую приёмку. Последние задания Qwen подготовлены в каталогах NI04.3/NI06.2/NI07.1. Публикации GitHub не было.

Доказательства: [group delivery](../../database/retailcase_ni061_group_delivery_20261012.md), [aggregation lifecycle](../../database/retailcase_ni043_aggregation_lifecycle_20261012.md), [exception returns](../../database/retailcase_ni062_exception_returns_20261012.md), [financial revisions/summary](../../database/retailcase_ni071_revision_summary_20261012.md). API509 current, live Oracle VALID, protectedP20/H20 retained; saved return receipts replay after completed supplier/disposal, finance trip summary3GEL.

## Закрытый технический этап

**STOCK-CORE-V2 completed_dev_cutover**: RABAEV/orcl ACTIVE, B0-20261009-STOCK-V2, compatibility OFF; 25 ADAPTED / 6 RETIRED / 0 UNCONVERTED известных writers. Единая проводка, P/H/марки/доменные факты/journal/outbox, точная арифметика и direct-DML guards реализованы. Replay/competition/rollback подтверждены на ограниченных реальных случаях, WinForms/API обновлены.

Это не закрывает весь NI03, все 363 сценария или промышленную мощность. TASK_COMPLETE, WAVE_LAUNCH, CASE pick/short/move/return, QC, shipment и marked birth не ставятся на повторное написание. Полные CASE-return/shipping UI-сценарии, государственные квитанции ещё не объявлены принятыми. Положительный маркированный inventory birth адресно подтверждён в NI03.2; это не полная промышленная приёмка.

Статусы разделяются: технический этап завершён; реализованная часть с остатком; недостающая функция/конфигурация; существующий код без достаточного подтверждения. Отсутствие приёмки не означает отсутствия кода.

## Направления и остаток

| NI | Уже есть | Остаток |
|---|---|---|
| NI01 | ARTMAS10/file gateway/receipt/label/putaway/ACK | NI01.1 — реальный SAP-контракт и пробелы правил |
| NI02 | SAP→существующая СТ→готовое назначение | NI02.1 exact auto через прежний writer реализован в dev; NI02.2 поздние заказы/ограничения |
| NI03 | ACTIVE core/task/wave/CASE | NI03.1–3 — допуск, переходы заданий, фактический fulfillment |
| NI04 | CRPT aggregation/CASE/unit identity/birth | NI04.1–3 — матрёшка, способы отбора, сквозная маркировка |
| NI05 | Native QC/LOT_CHECK/CASE→СТ/shipment | NI05.1–3 — версия допуска, погрузка/выезд, магазин |
| NI06 | CASE return и supplier return adapter | NI06.1–3 — два плеча, бизнес-возврат/потери, тара |
| NI07 | Счета/тарифы/пересчёт | NI07.1–2 — складские статьи и сверка |
| NI08 | VRP/матрица/Ганта/pick faces | NI08.1 — прогноз по фактам и рекомендации |

## Очередь исполнения

NI03.1 реализован/подтверждён адресными dev случаями ([evidence](../../database/retailcase_ni031_stock_eligibility_20261009.md)); на дату начала редакции общий architecture gate был красным по прежнему debt. После149 gatePASS с уменьшенной baseline/0cycles. **Текущий — [NI03.3](execution/active/ni03_3.md); NI07.2 остаётся незавершённым; реализованные части остальных спринтов и открытый остаток отражены в JSON и последних ticket-записях.** Из 18 спринтов редакции: 1 реализован, 17 остаются. Порядок ниже приоритетный; dependencies задают вход результата. ERP-контракт можно готовить независимо от HU. Обязательный внешний gate маркированного SKU не обходится ради порядка; он добавляет условие NI04.3 к зависимым отгрузке/возврату.

| № | Спринт | Результат оператора | Зависимости |
|---|---|---|---|
| 1 | [NI03.1 — Доступность товара для планировщиков](execution/active/ni03_1.md) | Допустимые источники и конкретная причина отказа видны оператору; карантин не даёт резервировать/отбирать товар, P сохраняется. | ACTIVE core и существующая основа |
| 2 | [NI03.2 — Исполнение и восстановление складских заданий](execution/active/ni03_2.md) | Задание показывает остаток и следующее действие; DONE отражает подтверждённый факт; повтор/переназначение не дублирует движение. | NI03.1 |
| 3 | [NI03.3 — Фактическое исполнение заказа и волны](execution/active/ni03_3.md) | Видны собранные количества/места и дефицит; подготовленная СТ не означает PICKED. | NI03.2 |
| 4 | [NI04.1 — Складская матрёшка грузовых мест](execution/active/ni04_1.md) | Паллета движется с коробками/единицами; листья, масса и машиноместа не считаются дважды. | NI03.2 |
| 5 | [NI04.2 — Недостающие способы комплектации](execution/active/ni04_2.md) | ТСД ведёт способ отбора; фактические партия, количество, масса и состав входят в ту же проводку. | NI03.3, NI04.1 |
| 6 | [NI04.3 — Сквозная маркировка и внешние адаптеры](execution/active/ni04_3.md) | Код сохраняет происхождение/позицию до возврата; несколько профилей не увеличивают P; локальный журнал не выдаётся за государственный ACK. | NI04.1, NI04.2 |
| 7 | [NI01.1 — Правила приёмки и реальный файловый SAP-обмен](execution/active/ni01_1.md) | По SAP-заказу приняты фактические паллеты с идентификатором/количеством/партией/сроком; создано размещение и квитанция. | NI03.1 |
| 8 | [NI02.1 — Автоподготовка через существующие writers](execution/active/ni02_1.md) | SAP-заказ получает прежнюю подготовку СТ; назначение рейса остаётся существующим. | NI01.1 |
| 9 | [NI02.2 — Поздние заказы и транспортные ограничения](execution/active/ni02_2.md) | Диспетчер видит решение/ограничения заказа; использует готовое назначение рейса. | NI02.1 |
| 10 | [NI05.1 — Контроль и допуск версии состава](execution/active/ni05_1.md) | Изменение состава отзывает допуск; подтверждается актуальная версия. | NI04.1, NI04.2 |
| 11 | [NI05.2 — Экспедиция, погрузка и выезд](execution/active/ni05_2.md) | Закрытие по погруженным местам; запас списывается существующей командой один раз, погрузка/выезд различимы. | NI05.1, NI03.3, NI02.2 |
| 12 | [NI05.3 — Приёмка магазина и расхождения](execution/active/ni05_3.md) | Магазин подтверждает доставку и акт расхождения, история отгрузки/марок сохраняется. | NI05.2 |
| 13 | [NI06.1 — Межскладской поток двух плеч](execution/active/ni06_1.md) | Для места видны оба плеча и физическая ответственность. | NI05.2 |
| 14 | [NI06.2 — Бизнес-возвраты и расследование потери](execution/active/ni06_2.md) | Возврат — отдельная разрешённая проводка; поиск потери сохраняет историю. | NI05.3 |
| 15 | [NI06.3 — Баланс оборотной тары](execution/active/ni06_3.md) | Отдельный баланс тары без смешения с товарным P и двойного машиноместа. | NI05.3, NI06.1 |
| 16 | [NI07.1 — Затраты RETAILCASE поверх биллинга](execution/active/ni07_1.md) | В существующем счёте объяснимо рассчитаны новые статьи. | NI05.3 |
| 17 | [NI07.2 — Сверка фактов и закрытие дня](execution/active/ni07_2.md) | Сверка объясняет незакрытые обязательства, без скрытого UPDATE запаса. | NI06.2, NI06.3, NI07.1 |
| 18 | [NI08.1 — Прогноз и рекомендации по исполнению](execution/active/ni08_1.md) | Рекомендации объяснимы и утверждаются; solver/карта/Ганта сохраняются. | NI07.2 |

## Правила исполнения

- Минимум 80% ресурсов на функционал. Сначала открыть конкретный existing caller и пункт ТЗ редакции 57; реализовать только подтверждённый gap. Один ticket — один/два связанных сценария, обычно 3–8 файлов. Каждый способ отбора/внешний адаптер — отдельный ticket.
- RABAEV, существующие документы/права RUSERS и public→application/domain→infrastructure сохраняются. Inventory владеет stock-командой; единственная физическая транзакция — RRL_STOCK_POSTING_API. Второй stock registry/engine не создаётся.
- Карантин через недоступные ячейки хранения/отбора, P сохраняется. Размещение минимизирует время будущего пополнения с учётом расстояния/условий. Прямой отбор разрешается явной стратегией, не произвольным обходом допуска.
- SAP S/4HANA 2020 Retail: ARTMAS/ARTMAS10, XML-файл шлюза. Приёмка только по SAP-основанию, адресат склад. Количество/партия/срок фиксируются на реальной паллете; идентификатор допускает SSCC и внутренние значения.
- Маркировка/профили/разрешённое сканирование настраиваются в WMS SKU. CRPT/табак, ЕГАИС и другие системы по применимости; несколько профилей одной единицы не увеличивают P. QR единицы не заменяется EAN товара. Состав/партии/коды/версия сохраняются во всех stock-спринтах. Локальный journal/outbox не считается государственным ACK.
- Готовые приёмка, назначение рейсов, волны, mini-max, CASE, инвентаризация, QC, TMS/VRP/Ганта/billing не пишутся заново. По решению владельца13Oct auto-split реализован самостоятельно через прежний writer; архив2011 не применяется.
- Проверки адресные: изменённое действие/эффект и существенный отказ/replay/concurrency. После meaningful case — решение по slow SQL. Авторский тест не заменяет независимую приёмку; неподтверждённые сценарии не отмечаются passed.
- Сроки/бюджеты не измерены. Старые 175–304 дня и GPU qualification не блокируют работу и не становятся обещанием. Большие load/recovery/пилоты после рабочего функционала и отдельного решения владельца.
- NS00 сохраняет среду; NS01–NS04 идут внутри функции; NS05 отложен. NS06/07/09–12 — адресные работы по необходимости, NS08 использует установленное ядро. NS50/NS61–NS67 — будущий выпуск/пилоты.
- ТМС-2 имеет самостоятельный план; здесь его 17 спринтов не переписываются.

[NS-каталог](sprint_plan.md) · [полные 363 сценария](execution/execution_plan.json) · [маркировка](track_trace_coverage.md). GitHub этой редакцией автоматически не обновляется.

## Продолжение 09.10.2026

NI03.2 и связанный NI03.3 в работе. Установлены 029–037, исполнение CASE/SHIP в BASE, частичная подготовка существующей СТ без изменения исходного заказа, продолжение пополнения целыми паллетами и явные моменты смены/инцидента. См. [подробный статус](../../database/retailcase_ni033_execution_20261009.md). Следующий стык: отдельное разрешение отбора после пополнений; затем альтернативная ячейка и FULLPAL. Независимая и промышленная приёмка остаются открытыми.

040–043: FULLPAL physical binding/pinned whole shipment и явное покрытие wave PICK release реализованы. Открытая функциональная очередь — сегментация CASE на несколько адресов с передачей существующего HARD и lifecycle завершения wave/control; NI03.2/NI03.3 остаются in_progress. См. [статус](../../database/retailcase_ni033_fullpal_20261009.md).

Continuation 09.10.2026:044–048 native per-source multi-face/shared arrival and target HARD replacement delivered;049 actual wave blockers/finish delivered. Current functional ticket NI04.1 existing HU topology. Remaining NI03 complete CASE/control/short/multi-place acceptance and partial/multiple-target replacement stay explicitly open. See database/retailcase_ni032_target_supply_20261009.md, database/retailcase_ni033_wave_finish_20261009.md and database/retailcase_ni041_hu_design_20261009.md.

### 10.10.2026 — NI04.1/NI05.1 slices065–067
Существующие CASE получили фактические состояния контроля и отзыв допуска при unpack. CASE-only верхнее HU отгружается одной root транзакцией через существующие ST, с историей и освобождением места. Own12+8/replay прошли; полные NI04.1/NI05.1 открыты (ordinary/FULLPAL leaves, route/dock consistency, concurrency/partial failure/marked/browser, packaging/labels/corrections).

10.10.2026:080–084 actual trip membership/legacy HU reconciliation/frozen store destination/full ordinary store receipt implemented and bounded author evidence recorded. Current next slice is store photo archive and weight/discrepancy workflow; full and external/independent acceptance remain separate.

10.10.2026:091 NI06.2 расследование реализовано через существующий Root, два независимых заключения и КРО без второго списания P; утверждённые возвраты и SAP/marked продолжаются.

10.10.2026:092–104 NI06.2 ordinary approved/SAP-file/driver custody/warehouse birth/existing putaway and NI06.3 quantity/deadline/damage/booked actual cargo/FULLPAL/shortage slices delivered. Full residual sprint acceptance remains open; current functional work continues NI06.3/NI06.2. Local changes not published.

10.10.2026:105–109 quantity tare loss/independent decisions/current holder debt and vehicle, complete-good BOX return24→configured picking, existing supplier ST/physical load1/departure/documentary handover delivered. Current NI06.2 ordinary disposal and marked lifecycle remain; full sprint acceptance not inferred from tickets.

10.10.2026:110 ordinary disposal through original core/loss original store and111 finance actual physical BOX norm/charge/version preservation delivered. Current functional NI07.1 extra expenses; marked/interwarehouse/other preserved residuals remain explicitly open.

10.10.2026:124..132 sender graph/UNIT-MIXED/current source warehouse/internalID/regulatory simulation boundaries/composition provenance delivered;133 NI08.1 started with actual execution forecast. Current resource/slot recommendations and common plan validator remain; all residual sprint acceptance tracked individually, not inferred from author slices.

NI08.1 author139: existing cluster one native UOW/current scope/immutable original TT/source/idempotent operation and client pending. Concurrent sameID creates one33528, changed request409, native caught error rollback; full timing/coordination/NS59/independent acceptance remain open.

10.10.2026:154–155 existingoutbox awarelease/fencing/atomic response+event/auditedretry and durablelocalresponse recovery delivered. No externalGov/SAP acceptance inferred. Current NI08.1 resource/range approval/drain/common timing validator, then remaining functional residuals per active cards. All17 open remain open until complete business result, not only author slice.

## 11.10.2026, редакция12: фактическое продолжение
17 открытых полных результатов не объявляются принятыми по числу tickets. Статусы planned_delta с уже записанными implementedSlices исправлены на in_progress_bounded_dev: отсутствие независимой приёмки не равно отсутствию функций. Исторические упоминания текущего NI08.1/NI04.2 относятся к прежним этапам; текущий функциональный фокус теперь NI06.1.
217–224 NI05.2/NI06.3: исходная целая паллета выгружается/восстанавливает исходный HARD/FF/version/task/UID, требует свежего QC и повторно грузится готовым механизмом. Тара — отмена непринятого предложения, реальные две стороны возврата/новое закрепление исходного CASE/HU/FULLPAL, ограниченная повторная цепочка на одной погрузке. Текущая опубликованная топология/измеренный слот/вместимость для всех корней; самостоятельная погрузка освобождает слот атомарно. Текущий склад перед просмотром/первым проведением/старым replay; actual3/P3H3↔P0H0, тара total1, исходные журналы сохранены. Native VALID; quality24/bothTS/557cycles0debt76; отдельные файлы Qwen подготовлены, независимые результаты не подменяются авторскими.
Проверка существующей приёмки: receiving.js уже показывает suggested_pallet_count/norma_ukladki/remaining_qty и разрешает фактическую укладку. Второй рекомендатель паллет не создаётся.
Исторический пробел на этапе217–224 (закрыт последующими284–447) — marked source: RRL_INTERWARE_PLAN_GUARD и RRL_STOCK_INTERWARE_REC явно запрещают marking profiles/unique units. Расширить оригинальный самостоятельный STOCK/FULLPAL маршрут с точным исходным unit fingerprint, затем фактическую приёмку/размещение/второе плечо; матрёшка отдельно. Реальные внешние ACK/оборудование остаются собственными фактами, не заменяются TEST.
По прямому указанию владельца первая остановка — после полного фактического завершения спринтов либо 12.10.2026 06:00 МСК (03:00 UTC). До этого функциональные задачи исполняются последовательно. Публикация GitHub не разрешена этой редакцией.

11.10.2026, редакция13 учёта исполнения: исправлены устаревшие planned статусы NI07/NI08 по уже существующим111–119 и133–250. Это сверка прогресса, без объявления всех сценариев принятыми или изменения18increments/363scenarios. JSON — актуальный currentSprint; старые начальные статусы в отдельных карточках остаются исторической датой создания, последующие ticket записи отражают выполнение.

Revision18 /512–520: NI07.1 ordinary BOX physical packing clock and separate actual assembly date rows delivered; one source claim preserves once-only charge. Actual new CASE2.75/BOX2.25 and immutable5 old lines13.50; two-date model8.50, physical multi-date rehearsal not claimed. Remaining transport/point/unload norms and real/independent acceptance stay open.

Revision19 /529–548: existing tariff publication with immutable period/currency/type/size/unload rates; actual system unload start →original STORE543 customer3/manual/no-loader, start-day reconciliation1/1/open0. Metadata publication does not claim monetary recognition. Next NI07.1 transport charges and NI06.3 actual tare cycles. All18 acceptance remains incomplete; GitHub authorized only after completion, SAP excluded.

Checkpoint550: добавлены публикация и история транспортных норм в действующем биллинге, сохранение точной операции и исправление после подтверждённого отказа; восстановление повреждённого локального начала выгрузки через сервер. Начисление транспортных расходов остаётся открытым.

Checkpoint555: NI06.3 — повреждённая тара после магазина возвращается по исходнику DAMAGE через прежние подтверждённые передачи, затем списывается на складе-владельце независимым решением; actual553/late rollback554. Открыт UI магазина/водителя и независимая приёмка.

Checkpoint558: существующая панель TarePanel дополнена выбором акта повреждения и актуальными подписями, без отдельного портала. Требуется операторское подтверждение ролей/восстановления, финансовая проводка транспорта остаётся следующей доработкой.

Checkpoint564: классы/габариты в существующем автопарке, версия и исходный hash, источник оригинального выезда установлен. Проверена метадата на отдельной машине; реальный выезд и денежная проводка остаются открытыми.

Revision24 /582–591: shared native Q26 monetary recognition/current rights/version/departure claim; actual107.25 race winner and atomic rollback, old carrier PRICE unchanged, original generic finance export without external ACK; existing billing and same day-board extended. Multiwarehouse/correction/real financial ERP and independent acceptance remain. All18 not declared complete.

Revision25 /598–611: нормативная коррекция переиспользует действующие независимые согласования и signed allocation. Actual original107.25/current0, two full credits one winner/other stale rejection; original monetary base and stock unchanged. Remaining multiWARE/physical mixed-day/real ERP/independent acceptance, all18 not closed.

Revision26 /615–616: live loading core enforces one physical warehouse/dock per current departure. Не создавать новое многоскладовое ядро одного TT; разные склады объединяются по рейсам счёта существующими scoped источниками/суммами. Ранее внесённый пункт multiWARE-in-TT удалён как избыточный. Результаты Q26 recognition/correction остаются, реальные недостающие сценарии остальных карточек сохраняются.

## Revision27: текущие изменения631–648
NI03.2: частичная замена нескольких собственных HARD в существующем native wave, один оставшийся целый physical source; P неизменён/чужой owner сохранён.
NI06.2: registered BOX возврат и неизменённая полная исходная PALLET с прежним UID проходят existing approval/SAP/handover/pickup/receive/PUT; actual643 P3H0/3keys6codes. Новый UID со старым PALLET кодом отвергнут. UI поддерживает заданный в товаре UNIT/BOX/PALLET/UNIT_OR_AGGREGATION.
NI08.1: непрерывное наблюдаемое вождение между рейсами/через полночь входит в прежние driver-day/Gantt/coordinator; explicit REST из существующего правила. Предыдущая смена/внешняя работа/правовые нормы не подтверждены.
Все18 спринтов ещё не завершены. Оригинальный auto-split NI02.1 требует исходника или решения владельца о восстановлении на existing preparation; вопрос задан. Full GitHub publication выполняется после завершения, SAP/SAP_INTEGRATION исключаются.

Revision28/checkpoint676: NI06.1 whole mixed UNIT+BOX+PALLET receiving implemented through original native multi-leg validator, per-physical-UID direct-mode scope. Actual673 twoSKU3each/six original units/nine codes/oneTOP/native rollback/replay; HTTP675 exact replay/current card modes. Partial groups and independent/browser/external gates remain. Source bundle includes667/674; never apply whole ACTIVE bundle.

Revision29/checkpoint682: existing QC label/red tag680–681 with current native actor/status/signature, stale409/no-store and scoped print UI. No new QC/stock writer. Actual green/hardware/attachment lifecycle and full acceptance remain open. NI06.3 stale not_executed acceptance metadata corrected to recorded bounded author cases, no independent acceptance fabricated.

Revision30/checkpoint690: real internal UID47 SAP receipt+existing PUT DONE/P3H0/3units6codes/truthful SSCC NULL; old SSCC receipt replay unchanged. Header registration/quantity executor reused. External activation/hardware/full independent acceptance remain open.

Revision31/checkpoint715: mixed-profile group completes existing placement/custody/ST/QC/load; store aggregation extension next. Inspection700 delivered, no automatic day closure or complete sprint claim.

Revision32/checkpoint724: mixed group store acceptance3+3 via existing resolver/projection; native716/722 and UI718. Further independent evidence/real ACK/hardware open. No all-sprint closure.

Revision33/checkpoint747: original whole flat prepared ST may move to next planned trip preserving P3H3 and completed pick. Waiting physical task/CASE/nested/frozen onward revisions stay open. Actual source688 reused, no rebirth.

Checkpoint766 NI07.2: явная ячейка ожидания в существующих настройках и форме. Штатный physical task handler ещё открыт; статус спринта не изменён.

13.10.2026 revision34: NI03.2 multiple distinct retained sources834–837 uses existing sequential continuation, actual own rebind/pallet arrival/next demand/current target owner12+other8/exact repeat, own cleanup and nativeVALID. [Source/evidence](../../database/retailcase_ni032_sequential_sources_20261013.md). Capacity/second arrival/independent remain; 1 implemented dev increment,17 open. Latest owner continuation deadline20:00MSK13Oct or all complete.

Checkpoint916: NI01.1 per-item gatewayv2/shared canonical legacy row/current receipt UI, actual908/911; all18 остаются незавершёнными. [[database/retailcase_ni011_supply_lines_20261013]].

Checkpoint934: NI03.3 execution current scope/single snapshot и NI01.1 exact receipt recovery, report14; старые172/173 read-only3/remain0 и3/remain1, источникнепересоздавался. [[database/retailcase_ni033_order_execution_20261013]].

Checkpoint972: NI07.2 standalone CASEwaiting реализован953–971, реальный task1110/1111/12+8EA HARD сохранён; report16/screenshot18. Полный спринт открыт. [[database/retailcase_ni072_case_wait_20261013]].

Checkpoint984: original CASE mover/current boundFFsameTX and repeatedwaiting self-source1132/CT4FF4/12EA implemented, report17. [[database/retailcase_ni033_case_bound_move_20261013]]. Полные спринты открыты.

Checkpoint991: multipleCASEsameST implemented986/actual987 task1136/1137,12+8EA/HARD, independentchildsource. Report18; nested/mixed/capacity/day residuals.

Checkpoint999: HU binding993 реализован/VALID. Actual1138 переместил20EA в1HU,996 выделил12EA/версия6. UI состава/упаковки997998 и screenshots19–21, отчёт19. ПолныйNI04.1 открыт.

Checkpoint1014:1001/1002 CASEslot/FF10/P20H20; currentplacement/read/recovery/internalCASE/UI. Report20/screens22–23;fullNI04.1open.

Checkpoint1033: статусы/UOM/резерв/широкийэкран/scopedfulfillment/currentCASE/readguard/deeplink. Original1931 3+1, current2133CASE10FF10; report21/screens24–26. ПолныйNI03.3 открыт.

Checkpoint1039: позиция поставки/alias/closedview/labelguard/confirmedRefresh, actual908 readonly/currentprofiles/Node9471036/report22/screens27–28. Полные сprints не закрывались без результата.

Revision45/checkpoint1044: общий список/карточка заказов подключены к текущему native warehouse scope, exact quantities/UOM UI, report23/screen29; NI03.3 in_progress. Владелец поручил продолжать после20:00 до фактического завершения, прежний срок больше не действует.

Revision46/checkpoint1068: nested allCASE oneHU waiting via existingRoot/HU tasks, actual1149DONE1HU/20EA/P20H20/CTFF12+7/queueUI/http/replay; clock slottedrepack actual bug fixed. FullNI07.2/NI04.1 remainin_progress; twoHUlevels/mixedplaces/targetslots/external gates next.

Revision47/checkpoint1074: actualdeepPALLET→ROLL_CAGE→twoCASE/1152DONE1HU/P20H20/ROWbusy20840 .191sec/unchanged no-move result. DeepnestedoneTOP gap addressed; remaining multipleTOP/mixedFULLPAL/targetslots/interWARE/independentexternal. Report26/screen32, all18 notclosed.

Revision48/checkpoint1089: per-place native atomic selector, actualHU+CASE andtwoTOP/20EA/siblingindependent/sharedWAIT scopedguard/current UI/read/report27/screen33. Fullsprints remainopen; mixedFULLPAL/targetslots-capacity/external/independent remaining.

Revision49/checkpoint1098: bounded wave currentCASE/location/version/QCactions, existingQC ARM separate scan/weight/readonlylinks and response correlation/currentactor guards/report28/screens34+37. Wave553 stillblockedcorrectly; physical20/hard20 no writes, fullsprints remainopen.

Revision50/checkpoint1106: shared QC storage/strict pending-draft schemas/read-only recovery/fresh status after cachedPLAN/bounded scan correction; report29/screen38. No nativeQC or inventory mutation. Fullsprints remainopen; continue original remaining workflows.

Revision51/ownerdecision1108: актуального autoSQL нет; прямо разрешена безопасная самостоятельная реализация NI02.1, с переиспользованием current ORDERS/SBORKA writers/readyassignment. Текущий ticket NI02.1. All18notcomplete; старые missing-original ограничения исторические, destructive2011body не применять.

Revision52/1125: NI02.1 automatic_layout/shared writer/preview-run-resolve/durable UI delivered targeted dev. Actual2135 mixed2places/exact36EA/race/rollback/stale/replay, report30/screen41. Independent full acceptance отдельно; все18 не объявлены завершёнными. Следующий ticket: текущий physicalCASE label→готовыйQC источник, без нового контроля/проводки.

Revision53/1130: physicalCASE label→existingQC currentsource delivered/report31/screen42; noQCPOST/nativehandler unchanged. NextNI02.2 remaining transport-source constraints. Full independent/external acceptance not claimed.

Revision54/1145: existingwarehouseSKU tempview/public/currentTMSpreflight and exact conflict/unknown delivered/report33; SQLrewrittenbounds. Numericvehicle envelope/currentthermalfact/nativephysicaladmission remain, nofakecoldprofile.

## 14 октября: температура укладки и профиль автомобиля /revision55

V2 автоподготовки разносит несовместимые/неизвестные требования по местам; V1сохранённые результаты неизменны. Числовые возможности автомобиля добавлены в существующий версионный профиль, точный транспортный preflight/API/UI/nativecase1152/report34/screens45–46 подтверждены. Полный NI02.2 не закрыт: далее фактическое измерение и проверка перед товарным эффектом в существующих loading/departure commands. Число завершённых полных спринтов не увеличено.

14.10 /1200: физический TOP/type через прежний LOAD Root/DEPART завершён в bounded dev1195/1196, typed loaded planner mapper1197 installed. [Report37](../../../reports/retailcase/2026-10-13/37-physical-top-tare-report.md). Остаток NI02.2: тип полной STOCK-паллеты без HU/CASE, новый typed late-assignment, deadline сборки/ворота; полные спринты не закрыты.
