# WMS Admin UI Reference

Raw visual reference for the future WMS admin panel.

Source context:

- accepted by user on 2026-05-17 from the chat screenshot
- visual direction: `WMS PRO` style, dense operational admin dashboard
- target implementation stack: React + Ant Design, aligned with `C:\WEB\demand_forecast\demand_forecast_frontend`

Files:

- [`index.html`](index.html): static raw prototype of the accepted dashboard style
- [`styles.css`](styles.css): visual tokens and layout rules
- [`api-audit.js`](api-audit.js): lightweight API journal/replay block for the raw prototype
- [`external-outbox.html`](external-outbox.html): separate external outbox and adapter journal administration page
- [`external-outbox.js`](external-outbox.js): lightweight external outbox list/detail/retry logic
- [`bom.html`](bom.html): separate BOM recipe administration page
- [`bom.js`](bom.js): lightweight BOM list/detail/lifecycle/calculation logic
- [`customers.html`](customers.html): customer registry, customer card, addresses, legacy mapping, and customer picking rules
- [`customers.js`](customers.js): lightweight customer list/detail/edit/rules logic
- [`customer-orders.html`](customer-orders.html): customer order registry, legacy import, order rows, and fulfillment facts
- [`customer-orders.js`](customer-orders.js): lightweight customer-order list/detail/import logic
- [`product-shipment-settings.html`](product-shipment-settings.html): article-level aging norms for finished-goods shipment readiness
- [`product-shipment-settings.js`](product-shipment-settings.js): lightweight settings list/detail/save logic

Design notes:

- fixed left navigation with product logo and operational modules
- compact top header with search, notifications, help, and user profile area
- KPI strip with eight compact metric cards and sparklines
- main work area split into production, raw-material warehouse, finished-goods warehouse, and warehouse settings panels
- [`api-audit.html`](api-audit.html) is a separate administrative page, not part of `Главная`
- [`external-outbox.html`](external-outbox.html) is a separate administrative page for Mercury/CRPT outbox diagnostics and retry
- [`rights-admin.html`](rights-admin.html) is a separate rights administration page backed by legacy `RUSERS` / `USER_GROUP` / `RIGHTS`
- [`bom.html`](bom.html) is a separate MES recipe/BOM page protected by `bom_view`; lifecycle buttons require `bom_edit`, `bom_approve`, `bom_block`, or `bom_make_primary`
- [`customers.html`](customers.html) is protected by `customer_view`; customer card changes require `customer_edit`; rule creation requires `customer_rule_edit`
- [`customer-orders.html`](customer-orders.html) is protected by `customer_order_view`; legacy import requires `customer_order_import`; fulfillment facts require `customer_fulfillment_view`
- customer and customer-order pages use the global admin session API base from `admin-auth.js`; the operator-facing duplicate API base field is intentionally not shown
- [`product-shipment-settings.html`](product-shipment-settings.html) is protected by `quality_batch_view`; editing aging norms requires `quality_batch_edit`
- API page lists calls from `GET /api/admin/api-calls`, opens details, runs dry-run replay, and can repeat selected ID or date ranges through `POST /api/admin/api-calls/replay`
- [`admin-auth.js`](admin-auth.js) adds login/password entry and hides the API page unless the user has `api_audit_view`; real replay requires `api_audit_replay`
- Login uses the legacy Oracle user table `RUSERS`; the seeded local admin is `admin/admin123`.
- left navigation has fixed sidebar width, fixed row sizing, stable scrollbar gutter, and CSS pixel icons with a fixed icon slot to avoid visual jumping between pages
- retail demo customers are repaired/seeded through `scripts/seed-retail-customers.py`; do not seed Russian text through inline PowerShell commands
- light background, thin borders, small radii, dense tables, restrained blue/green accents
- no destructive database actions are represented in the raw prototype

This folder is a raw source/prototype. The maintained synthesis belongs in `wiki/`, and the future executable admin frontend should live outside `wiki-raw`.
