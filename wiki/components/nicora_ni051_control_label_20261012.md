# NI05.1: этикетка текущего допуска и красный тег

Checkpoint680–681, 12.10.2026. Владелец inventory. Печатный документ формируется из прежнего RRL_STOCK_QC_GATE.status_json через существующий actor-aware OutgoingQuality.status.

GET /api/outgoing-quality/{identifier}/control-label требует прежнее outgoing_pallet_check и текущий доступ к складу. expected_signature сверяется с текущей подписью; изменение состава даёт409. Ответ HTML с Cache-Control:no-store. Печать не меняет QC, остаток, резерв или статус погрузки.

Зелёная этикетка выдаётся только для native ready=true и подтверждённой подписи состава из64 шестнадцатеричных знаков. Нет подписи — нет зелёной этикетки. rescan_required=true печатает красный тег повторного контроля. Иные неподтверждённые состояния печатают «Допуск не подтверждён». Указываются СТ, режим, подпись, основание, сформировавший пользователь и время UTC. Значения экранируются; изменение состава отзывает старый допуск по прежнему native gate.

Прежний outgoing-quality.js получил кнопку печати. После смены пользователя/API/СТ/подписи или нового поколения ответа старое окно закрывается. Печать читает свежий серверный результат; snapshot клиента не подтверждает допуск.

## Подтверждение
[681](../../scripts/check681_quality_label.py): живой HTTP выдаёт неподтверждённую этикетку для уже отгруженной source669; ложная старая подпись даёт409. Локально проверены зелёное/красное представления, запрет зелёного без подписи и экранирование. Native зелёный источник/физический принтер/наклейка/браузерная приёмка не заявлены. Записей P/H/QC/label stock нет.

Источники: [renderer](../../api/wms_api_server/app/modules/inventory/domain/quality_label.py), [API](../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py), [действующий экран](../../wiki-raw/wms_admin_ui_reference/outgoing-quality.js). Новые SQL отсутствуют; повторно используется исходное bounded native status чтение. Полный жизненный цикл печати/исправления/прикрепления и независимая приёмка ещё открыты.

1094: существующий QC ARM оформлен как отдельные сверка состава/вес, текущий допуск/версия/режим/независимость. qc_shipment link читает только GET status; не запускает PLAN автоматически. Старый pending/draft имеет приоритет. Response actor/API scope, exact operation/control identifier/signature andcross-tab raw compare защищают сохранённую команду перед очисткой. Авторская targetedproof/browser next, nativeQC rules unchanged.

1095: actual browser found linkedQC hidden inside old collapsed additionaloperations. Existing layout now opens only explicitly linked containedpanel and focuses after auth-ready. Screenshot35 initially showedqueue, notQC; preserve it as unsuccessful navigation evidence. Fresh visibleQC capture pending.

1098: native/currentHTTP1093 PASS; CASE20/13 sameQCversions, P20H20/553 notready. Browser34 waveactions/37 actualQC layout;1097 response/readonly/cross-tab/lateactor PASS. [Отчёт28](../../reports/nicora/2026-10-13/28-wave-qc-workflow-report.md). No QC writes/greenadmission/hardware/independent closure. DamagedQC intent recovery next.

1100 PREPARED UI recovery: shared wmsCommandIntent storage owner + separate QC contractvalidator; pending/draft damagedraw blocks newwrites. Read-only composition action separate fromPLAN; archive only after sameidentity freshGET beforedeletion. Exactoriginal command/raw retained andother-tabscans notdeleted. Native schema unchanged; runtime/JSfocused pending.

1104: separate bounded draft scan renderer (last50, counts notphysicalunits); barcode/profile and per-scan removal before confirmedcommand, same currentdraft/raw/scope guards. Pendingoriginalbody cannotbeedited; nativefullcoverage remainsauthoritative. Actual emptyunmarkedCASE screenshot next, no fabricatedscans.

1106: recovery/scan view/currentPLAN read implemented, authorJS1097/1102+1105 PASS; browser38 realcurrentCASE20/0scans/unmarked. No nativeQCwrites/browserdamagedstorage/hardware/independent confirmation. [Отчёт29](../../reports/nicora/2026-10-13/29-qc-recovery-scan-report.md). Fullsprint remainsopen.

1126: prepared read-only physicalCASE alias resolver (SSCC/CASE:ID→existing LEGACY_SBORKA_PALLET_ID/PALLET_UID). FreshRUSERS/nativeQCpermissions beforelookup, currentnativeassert allcandidates, ambiguousrefusal. Status returns requested_identifier onlywhenresolved; UI freezescanonical logical identifier before any command. Commands and cached pending do not re-resolve physicalaliases; existingnativeQC/stock handler unchanged. Runtime pending.

1130: read1127/HTTP1128 actualphysicalbarcode+CASE:1131+logical allcurrentCT20/readyfalse, unknownactor/source denied; UI1129 canonicalfreeze/retry/noautoPLAN PASS; screenshot42/report31. P20H20 unchanged/noDDL/noQCPOST. SQL11.433ms17buffers/17.32ms10 bounded3/UNIONexact retain/noindex ownerinventory. Full independent/weights/scanner acceptance not claimed.

## Контроль → существующая погрузка, 14.10

[Report64](../../reports/nicora/2026-10-13/64-ni051-quality-loading-link.md): текущий QC snapshot содержит назначение СТ при transport_dispatch_view; bounded2/неоднозначность не угадывается. При готовом допуске UI открывает существующий рейс. CASE1131→33635 read200, SQL4.174мс; UI states modeled,0POST. Новых назначений/допусков нет. Gate755/0/73,24tests/обаTS/encodingPASS.
