# Qwen: CASE контроль и упаковка065/066
Используй отдельную business warehouse/собственные документы. Не меняй общие остатки, настройки или историю.
1. Выполни scripts/ni051_case_control_case.py: реальные CASE12+8 из существующей волны, root cleanup только собственных P/H.
2. Проверь PLAN → CONTROL_IN_PROGRESS, BOTH scan pending → independent weight CONTROLLED; CONTENT_VERSION не изменён контролем. Failed weight → WAIT_CONTROL и full rescan. Replay тот же результат/нет второго event.
3. Nested CASE QC не списывает P/H, whole_hu_shipment_required=true. Распаковка отзывает обе подписи/ready и ставит WAIT_CONTROL обоим CASE.
4. Два соединения: QC vs pack/unpack/move; stale closure отклоняется, P/H не искажается, согласованный ST-before-CASE порядок. Не называй это доказательством отсутствия всех deadlocks.
5. Целое перемещение после контроля: approval состава сохраняется при неизменных goods/packing; марки, owners и quantities сохранены.
6. Проверь longest SQL, решение cache/bounds/index/backlog с владельцем. Независимую браузерную/бизнес приёмку отдели от выполненного сценария.
В отчёте actual operation IDs, events, до/после P/H и точные незакрытые случаи. Верхняя HU shipment ещё не реализована; не выставляй полный NI05.1 DONE.
