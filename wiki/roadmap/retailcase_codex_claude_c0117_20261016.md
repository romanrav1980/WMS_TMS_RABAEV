# Распределение после результата Claude C0116

Решение16.10 по прямому поручению владельца. Прочитаны последние K-0065/K-0066 и `RESULT_C0116.md`. Результат C0116 уже интегрирован; повторять ручной вес, прокси справки и UI планы не требуется. Старый блокер `recovery-shorts backend не READY` в CLAUDE_STATUS не описывает текущее scoped чтение; статус файла Claude не переписывается за него.

| Исполнитель | Следующая задача | Результат и граница |
|---|---|---|
| Codex | CASE-aware межскладская передача смешанной матрёшки | CASE/ST/fulfillment/тара/origin сохраняются, товар не приходуется дважды; существующие interWARE owners, текущие права источника и назначения. Затем отдельный handover поддерева магазину |
| Claude | C0117: обзор восстановления недостач у старшего смены | Типизированная выборка своего склада, этап пересчёта/пополнения, карточка и связь с волной, mobile390, tooltip и URL-справка; без новых изменяющих команд |
| Codex после передачи | Интеграция C0117, оставшиеся native права | Проверка прав/ошибок/областей и общего gate по итоговому срезу; manager/driver/dispatcher/finance/delegation остаются незакрытыми |

[[../components/retailcase_queue_scoped_read_20261015]] и [[../database/retailcase_inventory_task_scope_20261016]] подтверждают backend чтение, в том числе прежнюю положительную recovery строку. Текущий API — ограниченный список1–100 без total/cursor/has_more; пропущенный склад означает разрешённые склады, неизвестный склад403. Legacy даты без пояса. C0117 использует выбранный WARE и limit50, показывает границу выборки, не обещает полную очередь/UTC/SLA. Это явное отличие от прежнего запроса K-0063, не скрытая подмена контракта.

[Задание и locks C0117](../../coordination/retailcase-claude/TASK_C0117.md), [короткий промпт](../../coordination/retailcase-claude/PROMPT_CLAUDE_C0117.txt). Обмен — прежние CODEX_TO_CLAUDE/CLAUDE_TO_CODEX и RESULT/RELEASE. Получены ACK K-0067 и RESULT/RELEASE K-0068, [результат Claude](../../coordination/retailcase-claude/RESULT_C0117.md). Внутренние субагенты не создавались, повторный платный запрос не нужен.

Интеграция Codex: типизированный recovery UI принят; функция ShiftSupervisorDesk105 строк не прошла gate, состояние URL-склада и session→resource map вынесены в useShiftContext без расширения debt. Финальный gate PASS:1118 файлов/0 cycles/debt72,24 tooling/architecture tests, оба TS. Root повторил9 UI-проверок после refactor: [отчёт](../../reports/retailcase/2026-10-16/interware-case/root-ui/recovery_result.json); live empty/403, остальные состояния — browser fixtures, mobile390 overflow0, writes/errors0. Это не native positive recovery fixture.

Codex выполнил CASE-aware interWARE: ASM1EA + коробочный24EA + штучный1EA → исходная погрузка → межскладская приёмка/целое HU-перемещение → второе плечо → магазин PAPER_COUNT26EA. Ручной складской QC и frozen loading origin завершены, исходные заказы1/1 и25/25, остатки0/0, истории сохранены. [[../database/retailcase_interware_case_bridge_20261016]] содержит точные границы и SQL backlog. Передача части дерева нескольким магазинам, оставшиеся scoped write/конкуренция ролей и аппаратный пилот остаются отдельными незакрытыми работами; все спринты этим инкрементом не объявляются завершёнными.
