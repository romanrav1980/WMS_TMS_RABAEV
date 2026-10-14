# NI01.1: позиции SAP и рабочая приёмка

Checkpoint916, 13 октября.905 APPLIED, RABAEV/orcl; capture904/SHA/paired rollback. Version2 предполагаемого WarehouseSupplyOrder поддерживает разные LineNumber одного SKU, version1 сохраняет запрет. Это формат шлюза, не стандартный SAP IDoc; ARTMAS10 не меняется. WMS-профили маркировки сохраняются.

Source PK(order,line) сохранён, прежние UNIQUE ROW_ID и order/articul заменены lookup indexes. Legacy RRL_PRIHOD_NAKLAD_ROWS UNIQUE(document,articul) сохранён: одна каноническая строка с точной суммой планов BASE. SupplyLineWriter выделен из фасада, записывает только исходный план. Native Receipt CORE/PLAN уже работают по order/line, stockroot unchanged ACTIVE/compatOFF. Detail/quantity amendment/header completeness используют original POSTED_BASE_QTY/STOCK_BASE_UOM по order/line; неправильная baseline запрещена. Принятую строку нельзя удалить/уменьшить ниже факта. Shared legacy row удаляется лишь без ссылок.

DDL инвалидировал9 зависимостей; 003_compile восстановил их,907 USER_ERRORS[]/INVALID[]. Полного копирования БД нет. Rollback отказывается при уже существующих v2 shared rows, не удаляет данные; rollback не испытан.

Actual908: планы3+3, первая приёмка3 physical units/6codes CRPT/TOBACCO и EGAIS/ALCOHOL, первая accepted3/remaining0, вторая accepted0/remaining3. Cached root repeat/layout3, own reversalP/H0, protected688 stock/version unchanged. Actual910 такой же baseline; resume911 на сохранённом source910: revision2 canonical7(line3+4), accepted shrink3→2 refused atomically, revision3 delete unreceived line/canonical3 retained. Затем native own reversalP/H0.

Непрошедшие попытки:900 v1 rejected422 до данных;906 stale API v1 rejectedv2, rootserv.bat907 restarted hidden;909 amendment reversed908 correctly refused. Initial910 harness ошибочно загрузил ctx908, amendment и повторное сторно908 refused; resume911 использовал правильный сохранённый910 без новой товарной приёмки. Эти попытки не PASS; чужой запас не изменён.

Receiving894/912/915: responsive source/orders/lines/pallet, deep source link, current WMS profiles, busyfieldset/stale guard, кнопки выбора/keyboard/highlight, zero-remaining guard. Source detail содержит native incoming condition/receipt_allowed/state OPEN/COMPLETE/REVERSED/RECONCILED; closed source blocks new UI-confirm, reversed counts исторические. Browser896 protected688 auto-singleline/profile2/confirmdisabled screenshot14. Browser908 two-line counters screenshot15. Manual CUA selections не дали наблюдаемого результата, не сертифицированы; Playwright connector navigate hung/terminated, не PASS. Последний915 status browser ожидает.

SQL914: detail3.678ms/32buffers, canonical2.236ms/38, received0.765ms/18.13, completeness3.234ms/17.75. Retain <=1000 source lines/indexed order-line receipts (existing RRL_SAP_RECEIPT_LINE_IX)/canonical legacy key; no extra stock index/writer. Не промышленная нагрузочная приёмка.

Architecture691/0cycles/76 allowances PASS tightened down; Node receiving/context syntaxPASS. Encoding run21783 pending. NI01.1 full realSAP/ACK/concurrency/hardware/independent gates остаются; all18 not complete. Plan36/currentNI03.3, continue until20:00MSK13Oct2026. GitHub не публиковался.

[SQL](../../db/migrations/2026-10-13_ni011_supply_line_v2/apply.sql).

[Screenshot14](screenshots/14-sap-receiving-workspace.png) · [Screenshot15](screenshots/15-sap-two-lines-workspace.png).
