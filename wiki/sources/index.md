# Source Catalog

This page catalogs raw sources that the root wiki compiles from.

## NIKORA

- [nikora_agents_20260915.md](nikora_agents_20260915.md): источники агентного плана, ограничения локальных GPU, API-тарифы, 41 ТЗ и воспроизводимая проверка бюджета без амортизации.
- [nikora_ui_20260915.md](nikora_ui_20260915.md): требования 15 рабочих мест, быстрый ТСД/диспетчер ричтраков, источники переиспользования и 25 проверенных offline-рисунков.
- [nikora_20260915.md](nikora_20260915.md): ТЗ 1.3, XML 1.1.0, IT guide, операционные материалы Drive и код TMS/WMS; результаты проверки 15.09.2026.
- [Исходный комплект и probes](../../wiki-raw/nikora_analysis_20260915/): неизменённые исходники, ZIP и воспроизводимые изолированные проверки.

## Project Entry Points

- [`../../TMS.sln`](../../TMS.sln)
- [`../../.editorconfig`](../../.editorconfig)
- [`../../.gitattributes`](../../.gitattributes)
- [`../../.gitignore`](../../.gitignore)

## Root Documentation

- [`../../EXTERNAL_INTEGRATION.MD`](../../EXTERNAL_INTEGRATION.MD)
- [`../../NEW_BD_ENVIROMENT.md`](../../NEW_BD_ENVIROMENT.md)
- [`../../wiki-raw/wms_admin_ui_reference/`](../../wiki-raw/wms_admin_ui_reference/): accepted raw visual reference for the future WMS admin panel

## Main Application

- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj)
- [`../../MINI WMS/WindowsApplication2/WindowsApplication2/Form1.cs`](../../MINI%20WMS/WindowsApplication2/WindowsApplication2/Form1.cs)

## Terminal Contour

- [`../../MINI WMS/CS_CATClient/CS_CATClient.csproj`](../../MINI%20WMS/CS_CATClient/CS_CATClient.csproj)
- [`../../MINI WMS/CS_CATClient/FormMain.cs`](../../MINI%20WMS/CS_CATClient/FormMain.cs)
- [`../../MINI WMS/CS_CATClient/DBComponent.cs`](../../MINI%20WMS/CS_CATClient/DBComponent.cs)
- [`../../MINI WMS/Tserver/Tserver/Tserver.csproj`](../../MINI%20WMS/Tserver/Tserver/Tserver.csproj)
- [`../../MINI WMS/Tserver/Tserver/Program.cs`](../../MINI%20WMS/Tserver/Tserver/Program.cs)
- [`../../MINI WMS/DeviceApplication3/DeviceApplication3/DeviceApplication3.csproj`](../../MINI%20WMS/DeviceApplication3/DeviceApplication3/DeviceApplication3.csproj)
- [`../../MINI WMS/DeviceApplication3/DeviceApplication3/Form1.cs`](../../MINI%20WMS/DeviceApplication3/DeviceApplication3/Form1.cs)
- [`../../WMSTerm/постановка.txt`](../../WMSTerm/%D0%BF%D0%BE%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0.txt)

## Database Reconstruction

- [`../../db/windowsapplication2_xp12_oracle/README.md`](../../db/windowsapplication2_xp12_oracle/README.md)
- [`../../db/windowsapplication2_xp12_oracle/create_schema.sql`](../../db/windowsapplication2_xp12_oracle/create_schema.sql)
- [`../../db/windowsapplication2_xp12_oracle/01_tables.sql`](../../db/windowsapplication2_xp12_oracle/01_tables.sql)
- [`../../db/windowsapplication2_xp12_oracle/04_procedures.sql`](../../db/windowsapplication2_xp12_oracle/04_procedures.sql)
- [`../../db/windowsapplication2_xp12_oracle/gap_report.md`](../../db/windowsapplication2_xp12_oracle/gap_report.md)

## Publication Exclusions

- SAP/SAP_INTEGRATION projects are intentionally not cataloged for GitHub publication.

## NICORA приёмка и интеграция 7 октября 2026

[Редакция 56 общего ТЗ и проверка](../requirements/nikora_business_processes/editorial_review_v56.md) опирается на новое поручение владельца и разделы 7–9 Google Docs «Требования к интеграции ВМС Никоры с SAP ERP». [Текстовый снимок интеграции](../../wiki-raw/nikora_sap_integration_20261007/README.md); [исходный DOCX редакции 55](../../wiki-raw/nikora_business_processes_v55_20261007/Nikora_business_processes_v55.docx). Входящее основание — разрешённая поставка SAP, связанная с закупочным заказом. Синтез не подтверждает реализацию функций текущей WMS.

- [NICORA сквозная маркировка 07.10.2026](nikora_track_trace_20261007.md): поручение владельца, официальные различия табачных кодов и документооборота ЕГАИС, исходный SQL CRPT; ТЗ 57, модель RABAEV и 43 спринта. Внешние адаптеры и миграции ещё не выполнены.

- [nicora_ns00_environment_20261007.md](nicora_ns00_environment_20261007.md): NS00 — живой seed/reset/cleanup, rollback, fresh dependencies и restart evidence; пределы core fixture и незавершённые gates.
