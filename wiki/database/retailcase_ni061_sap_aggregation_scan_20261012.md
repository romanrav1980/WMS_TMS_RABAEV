# Межскладская приёмка: агрегации исходной SAP-поставки
Migration2026-10-12-311-sap-interware-aggregation APPLIED. Приватный RRL_IW_AGG_SCAN теперь разрешает composition из RRL_SAP_TRACE_AGG только через конкретную строку заказа фактической RRL_SAP_PALLET_RECEIPT, APPLIED SAP_RECEIPT stock operation, прежний UID рождения и положительное проведённое количество. NonSAP sender proof310 сохранён.

Каждый код раскрывается в старые physicalunit ID/quantity/raw code. Версия профиля в PROFILES_JSON прежнего code registry должна совпадать с текущей карточкой; это также усилено для nonSAP. BOX/PALLET/UNIT_OR_AGGREGATION проверяются прежним owner, точная матрица/duplicate/foreign/partialset и known regulatory invalidation сохраняются. Нового реестра кодов, родителя товара или quantitywriter нет.

Функциональный дефект прежнего импорта исправлен в integrations/infrastructure/supply_orders.py: setinputsizes задавал xml_raw, отсутствующий в INSERT aggregation. Теперь CLOB code_raw соответствует реальному placeholder. Ранее эта ветка возвращала DPY4008/HTTP500; после исправления реальный XML с двумя составами принят202.

Сценарий311: ARTMAS материал, XML SAPwarehouse supply3/2aggregations, native physicalbirth3/6codes, original autoPUT task completed, existingpick/ST/QC/LOAD/DEPART, interwarehouse2scans→3samephysicalunits. Native late rollback и actualHTTP replay, foreign/missing/duplicate aggregate отказаны. P3H0 в целевом приёмочном карантине, protected20H20. Source311 сначала отклонён до импорта ARTMAS, затем 500bind и SSCC evidence conflict исправлены; исправленный SAPfixture revision2 применён до physicalreceipt. Товар создан ровно один раз, контекст tmp/context311.json сохранён. Ранее ошибочный PALLET source code не зарегистрирован как physicalaggregation.

На freshfixture source311_marked_case содержит ARTMAS beforeSUPPLY и PALLET code=actualSSCC. Никогда не повторять source/resume/caseinitial для имеющегося context311; savedAPI exactreceipt replay допустим. Это не hardware acceptance/realSAPtest/legalACK.

SQL/source policies: exact receipt UID unique index and aggregate order-line PK retained; bounded20000 profile matrix. large1000 aggregation fanout measurement/rewrite backlog inventory from310 остаётся. После case311 требуется измерение актуального SAPproof SQL; не утверждать performance без него.

Источники: [native](../../db/migrations/2026-10-12_ni061_sap_aggregation_scan/apply.sql), [case](../../scripts/case311_aggregate_receive.py), [[retailcase_ni061_aggregation_scan_20261012]].
