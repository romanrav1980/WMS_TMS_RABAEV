# TMS Agent Onramp

This repository uses a Karpathy-style LLM wiki pattern.

Before making non-trivial project decisions, start here:

1. Read [`wiki/index.md`](wiki/index.md).
2. Open the smallest relevant synthesis pages.
3. Drill into raw project sources only when the wiki does not settle the question.
4. After learning something durable, update the relevant wiki page and append [`wiki/log.md`](wiki/log.md).

## Three Layers

1. Raw sources
   - Existing code, SQL, project docs, logs, screenshots, exports, and files under `wiki-raw/`.
   - Treat these as evidence. Do not rewrite them as part of wiki maintenance.

2. Wiki
   - Files under `wiki/`.
   - These pages are maintained synthesis: project maps, runbooks, decisions, incidents, and source catalogs.
   - Prefer `[[wikilinks]]` for conceptual links and normal markdown links for file paths.

3. Schema
   - This file and [`wiki/WIKI_SCHEMA.md`](wiki/WIKI_SCHEMA.md).
   - These define how future sessions should ingest, query, and lint the wiki.

## Maintenance Rules

- Raw sources are source-of-truth evidence; wiki pages are summaries and cross-source synthesis.
- Do not silently merge contradictions. Record them on the relevant page.
- Keep pages small enough to scan in a fresh session.
- Use stable names: `subprojects/`, `components/`, `concepts/`, `runbooks/`, `incidents/`, `sources/`.
- Every meaningful wiki change updates `wiki/index.md`.
- Every meaningful wiki change appends `wiki/log.md`.
- Oracle schema changes must be mirrored in `wiki/database/`, represented in SQL under `db/windowsapplication2_xp12_oracle/`, `db/migrations/`, or `db/compatibility_fixes/`, and verified against live Oracle after application.
- Do not publish SAP/SAP_INTEGRATION projects to GitHub. Treat any local SAP material as out of scope for this repository publication unless the user explicitly changes that rule.
- For local Windows runs, prefer root `serv.bat` for the WMS API server, root `front.bat` for the WMS admin frontend/raw UI reference, and root `terminal.bat` for the WMS terminal Web/PWA app. These scripts clear their target ports before starting.
- Pallet identifier fields are not SSCC-only fields. They must accept both standard SSCC values and other internal/legacy WMS pallet identifiers; label them as `Идентификатор паллеты` where possible.

## Активный проект: ТМС-2

**ТМС-2** (Transport Management System 2) — текущий приоритет разработки. Полная замена C# WinForms транспортного модуля на FastAPI + React. 4 блока, 17 спринтов:

| Блок | Спринты | Суть |
|------|---------|------|
| Диспетчер | 1–6 | Таблица СТ, создание/закрытие рейсов |
| MAP + VRP | 7–10 | Карта OpenStreetMap (Leaflet), авто-план через OR-Tools CVRPTW |
| ARM / Ганта | 11–14 | SVG-диаграмма Ганта, нормативы водителей |
| Биллинг | 15–17 | Счета по рейсам, Oracle-пакеты |

Ключевые документы:
- ТЗ: [`wiki/requirements/transport_dispatch_tz.md`](wiki/requirements/transport_dispatch_tz.md)
- **План спринтов (living checklist):** [`wiki/roadmap/transport_execution_plan.md`](wiki/roadmap/transport_execution_plan.md)
- Тестовые данные «Добра Цен»: `db/migrations/2026-05-23_dobrotseny_seed/` (seed 046+047, 77 адресов, 385 СТ, ✅ применён в dev)

Инструмент → спринты: **код-код ($20)** — спринты 1,2,3,5,6,10,14,15,16,17; **кодекс ($200)** — спринты 8 (VRP), 12 (Ганта); **КК+КС** — спринты 4,7,9,11,13.

Следующий активный спринт: **Sprint 1** (расширить `GET /available-sts`, таблица 16 колонок).

---

## Current Regulatory Layer

- Mercury and Honest Sign support now has a second additive layer: migration `2026-05-17-003-regulatory-lifecycle-entities`, package `RRL_REGULATORY_API`, Mercury sites/operations, shared regulatory journal, and CRPT circulation lifecycle.
- Keep future regulatory writes behind `RRL_PRODUCTION_API` or `RRL_REGULATORY_API`.

## Current API Audit Layer

- API calls are logged in Oracle table `RRL_API_CALL_LOG` through package `RRL_API_AUDIT_API` and locally in JSONL under `api/wms_api_server/runtime/api_audit/`.
- Replay is exposed only through `GET /api/admin/api-calls`, `GET /api/admin/api-calls/{id}`, and `POST /api/admin/api-calls/replay`.
- Admin/replay calls are logged but marked non-replayable to avoid recursive replay loops.
- The raw admin API audit UI is a separate page: `wiki-raw/wms_admin_ui_reference/api-audit.html`, not a panel on `Главная`.
- Admin rights are separate: `wms_admin_login` enters the shell, `api_audit_view` opens the API audit page/list/detail/dry-run, and `api_audit_replay` allows real replay.
- Admin users must be read from legacy Oracle `RUSERS`; group permissions come from `USER_GROUP`/`RIGHTS`. The local seeded admin is `RUSERS.ID=admin`, `PASS=admin123`, `USER_GROUP=GLOBAL_ADMIN`.
- Preserve the legacy rights semantics: `RRL_HAS_WRIGHT` treats `GLOBAL_ADMIN` as all-rights, and the API admin auth mirrors that with `*`.
- Rights administration is a separate raw admin page: `wiki-raw/wms_admin_ui_reference/rights-admin.html`. It uses `RIGHTS_ADMIN_VIEW` for read access and `RIGHTS_ADMIN_EDIT` for mutations.
- The audit/replay layer is the base for real Mercury and Honest Sign adapters: outbound adapter calls must keep certificate/signature metadata, queue/outbox status, request payloads, response payloads, external IDs, and retry diagnostics so failures in external services can be repeated and investigated.

## Encoding Discipline

- Repository text files are UTF-8. When reading Russian text from PowerShell, use `Get-Content -Encoding UTF8`.
- Before finalizing changes that touch Russian wiki/HTML/SQL/Python/JavaScript text, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1`.
- Oracle SQL migrations are UTF-8 too. Apply them with `tools/oracle_apply/OracleApply.csproj` default settings; use `--encoding=cp1251` only for a confirmed legacy Windows-1251 script.
- When a migration writes Russian seed/reference data, add or run a verification query for common mojibake markers before considering the migration clean.
