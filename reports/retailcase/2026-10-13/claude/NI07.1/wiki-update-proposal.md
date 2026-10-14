# Предложение wiki-обновления — NI07.1 (для интеграции Codex)

## Новая страница: wiki/components/retailcase_ni071_invoice_breakdown_20261014.md (предлагаемый текст)

```markdown
# NI07.1: расшифровка счёта и основания сумм

Код: admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx (встраивается в карточку счёта TransportDispatchPage), BillingCosts*.tsx/ts, BillingCosts.css.
Источники (только GET): /api/finance/logistics-costs/billing-orders/{id}/summary, …/transport-costs, /api/finance/expense-allocation/billing-orders/{id};
основания: /logistics-costs/warehouses/{ware}/rates/history, /logistics-costs/trips/{trip}/transport-cost-facts, /logistics-expenses/warehouses/{ware}.

- Сводка по валютам: категории раздельно, валюты не складываются, точная десятичная сумма внутри валюты.
- Основание любой суммы: источники и версия ставки; факты рейса с документами-доказательствами; документ расхода, решения, цепочка коррекций до исходного начисления.
- CSV всех оснований счёта из прочитанных данных.
- Узкая карточка: строки таблиц — карточки (container query).
- Ограничение: строка расхода счёта без WARE_ID/даты/решений — CONTRACT_REQUEST K-0007.

Отчёт: reports/retailcase/2026-10-13/claude/NI07.1/report.md.
```

## index.md — строка
- [NI07.1 расшифровка счёта и основания](components/retailcase_ni071_invoice_breakdown_20261014.md): валюты раздельно, источники и версии ставок, основание любой суммы, CSV оснований.

## log.md — запись
- 2026-10-14 / NI07.1 / Claude K-0008: расшифровка существующего счёта в features/finance Billing*; основания сумм по существующим GET, CSV оснований, узкая карточка; CONTRACT_REQUEST K-0007 (WARE_ID/дата/решения в строке расхода счёта). Авторская проверка, отчёт reports/retailcase/2026-10-13/claude/NI07.1.
