# Claude — статус C0095

Обновляет только Claude (отдельная сессия C0095, инструменты Read/Edit/Write/Glob/Grep).

**Статус:** RESULT / RELEASE (ожидание READY backend для живой проверки)
**Текущий блок:** реализация завершена: вход, выбор магазина, серверный список поставок (пагинация), карточка поставки, три режима приёмки BARCODE/WEIGHT_PHOTO/PAPER_COUNT (сервер назначает режим), сверка маркировки во всех режимах, повтор/восстановление после отказа/потери связи, offline-черновик, локальная справка на каждом контроле.
**Занятые файлы:** terminal/wms_terminal_web/src/features/store-receiving/** (25 файлов: contracts/api/messages/validation/hooks/photoApi/help/components/StoreReceivingApp/index/styles), docs/help/authoring/store-receiving-app.md, -barcode.md, -weight-photo.md, -paper-count.md, -recovery.md, reports/retailcase/2026-10-15/claude/C0095/report.md, coordination/retailcase-claude/CLAUDE_C0095_STATUS.md, coordination/retailcase-claude/CLAUDE_C0095_TO_CODEX.md.
**Не трогал:** другие UI, API/Oracle/main/vite/public/package, index/log wiki, git, прежние CLAUDE_STATUS/CLAUDE_TO_CODEX, proposals/C0095 (не понадобился — весь объём реализован кодом, не макетом).
**Последний прочитанный ID Codex:** C-0096 (coordination/retailcase-claude/CODEX_TO_CLAUDE.md).
**Открытые вопросы Codex:** см. CLAUDE_C0095_TO_CODEX.md — READY /api/store-app/*, и подтверждение, что существующие /api/delivery/store-receipts/confirm, /unloading/start, /api/delivery/store-photos/*, /api/delivery/store-scales/captures принимают новые store-app credentials. TypeScript/build/gate/Playwright не запускались мной (нет Bash/сетевых инструментов) — список нужных проверок в отчёте.
