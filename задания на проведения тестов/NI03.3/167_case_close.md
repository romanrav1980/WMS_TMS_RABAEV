# Qwen: закрытие CASE и реальный HTTP-отбор

Проверь scripts/ni033_case_close_existing_case.py: исходный1030SHIPPED сохраняет status/time/version/shipped operation; concurrent sameID one event/exact reply, changedbody409, open1031refusal, foreign403. scripts/ni033_case_close_guard_case.py проверяет20863 UPDATE/DELETE новых command-marker событий. Guard VALID, ledger migration2026-10-10-167-case-carrier-close APPLIED; не применять полныйcurrentbundle наACTIVE.

Сквозной author case scripts/ni033_case_http_close_flow.py использовал отдельныйWARE20052672/SKUQC16700CDC0EF51 и native good-tare count/book. Последний полный проход: revision233/wave402/CASE1037, CASE.HTTP167:1037 и CASE.CLOSE167.FIRST:1037. Реальные API claim/start/confirm1/replay/conflict, P2H1; header после line confirm остаётсяIN_PROGRESS, line statusPICKED. Close проверяет actualperline stock иWAIT_CONTROL. Injected journalfailure послеstate UPDATE откатываетboth/state+event; повтор close одинevent. Не предполагать один journalrow: compare before/after replay snapshot.

Goods cleanup native return/release/count; ownP0H0/goodtare0, originalWARE666 P20H20. Старые авторские attempts оставили ownwaves397–402 с unresolved cancellation/emptyCASE decisions; не подменять их статусDONE SQL. Требуется штатный разбор исходной потребности. Startup без booked goodtare возвращает409 объяснимыйcode вместо500.

Независимо проверь partial/SHORT_PICKED, несогласованную line status/quantity, физическое perline mismatch, разныеSKU/единицы, актуальный assignee/right/warehouse до replay и послеwait. Close metadata не проводит движение и не переоценивает товар; обязательные события в одномUOW. Данный author case не доказывает marked flow/hardware/government acceptance.
