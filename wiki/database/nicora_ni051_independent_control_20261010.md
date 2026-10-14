# NI05.1: независимый контролёр и политика допуска

063 APPLIED в RABAEV/orcl, QC_POLICY/QC_GATE/PALLET_QC_CMD и WARE policy guard VALID, checkpoints334–335. [Migration](../../db/migrations/2026-10-10_ni051_independent_control/apply.sql). Продолжает [[nicora_ni051_mark_quality_20261010]], полный спринт открыт.

В существующем RRL_RECEIPT_WARE_SETTINGS добавлены OUTGOING_QC_MODE и OUTGOING_QC_INDEPENDENT. Режимы NONE/ANY/SCAN/WEIGHT/BOTH; NULL наследует прежний BLOCK_IF_NO_PROOVE. Маркированный состав требует уникальных кодов независимо от режима обычного QC. Без новых настроек поведение обязательности обычного контроля сохраняется.

При independent=1 Root сравнивает authenticated actor с фактическими исполнителями: CASE physical lot creation operation/actor, FULLPAL confirmed warehouse move operation/actor. Editable SBORSHIK и assignment не считаются доказательством. Нет actual picking facts/несогласованные actors — нет положительного независимого контроля; GLOBAL_ADMIN автоматически не освобождён. Shipment перепроверяет автора сохранённого QC operation, поэтому включение независимости отзывает прежнее self-control разрешение.

BOTH требует два current composition results. Configured auto-shipment сохраняет первый успешный контроль, ожидая полного допуска; ещё не разрешённая отгрузка не стирает этот первый факт и не списывает запас. При полном допуске QC+shipment остаются одной root транзакцией. Authenticated QC actor должен иметь также существующее право shipment для фактической автоматической проводки; warehouse auto setting не выдаёт это право.

Existing receiving settings API/ARM расширены. Оmitted fields старого клиента сохраняют новые настройки; явный NULL mode возвращает legacy inheritance. Сохранение через прежнюю CONFIG X transaction/warehouse_settings_edit. Guard защищает новую warehouse policy от неавторизованного metadata изменения.

Own ni051_independent_control_case.py passed: actual admin picked3EA; GLOBAL_ADMIN+self и edited SBORSHIK denied; другой QC-only пользователь scan admitted/saved while BOTH waits weight; weight gives readiness; old settings payload preserves mode/independent; configured auto-shipment after explicit fixture shipment right, same operation replay/actual3EA and wave DONE. Own P/H cleaned root, fixture user soft-disabled, operation history retained. API schema exposes settings; JS syntax passed. Browser/CASE independent role/full sampling ещё не приняты.

Sampling percentage/persistent selected carrier, ordinary barcode full-composition evidence, exceptions/labels и native display/QR adapters — следующие tickets. Store/subwarehouse specific overrides не подменяются складской настройкой.

SQL policy and actual move actor reads bounded by warehouse/ST/CASE keys, максимум200 facts. Решение: существующие indexes/key predicates и bounded reads, новые индексы только при evidence NI08; отдельный load здесь не назначался.

SQL evidence063: actual move actors7d29mzz0xxazf ~0.66ms/21; warehouse insert3vw12kuyzbu2j ~3.74ms; DDL introspection283ms вне runtime. Existing bounds/key indexes retained, no new index.
