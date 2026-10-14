# NI03.2: частичное использование существующего target stock

059 implementation. [[retailcase_ni032_multi_target_supply_20261010]] покрывает весь owner из target UID. Теперь при неполном target coverage допускается уменьшить одну собственную storage HARD binding и связать её остаток с прежним физическим RT в той же root транзакции.

Первый ограниченный вариант: одна исходная owner binding, режим FULL_PALLET, целая исходная паллета помещается в remaining target capacity. Пример: target3 + storage20/H20 для заказов12+8; первый owner получает targetH3 и sourceH9, прежнее whole replenishment переносит20/H17. Target становится23/H20/free3; CASE подтверждает12+8. Не создаётся отдельная partial pallet с тем же физическим identifier в двух местах. Исходная целая паллета сохраняет identifier.

Если вместимости для целой подачи нет, или исходный owner разложен по нескольким bindings, этот slice не меняет резервы и оставляет прежний выбор подачи/альтернативной ячейки. HALF/partial physical splitting и marked-unit indivisibility должны подтверждаться отдельно. Source intent не очищается: после успешного rebind RT уже имеет remaining source reservation и существующий task-sync получает обычную готовую подачу.

059 APPLIED, RRL_STOCK_WAVE_CMD VALID, checkpoint327. Case ni032_partial_target_supply_case.py passed: target3 + source20/H20 -> target3/H3 and source20/H17 -> existing one whole task20 -> target23/H20/free3 -> native release/CASE12+8/replay. Face capacity17 cannot receive whole20: rebind leaves sourceH20/targetH0 unchanged; restore capacity27 then positive flow. Existing source intent, actual task-sync and real CASE used; no second task engine. Own stock/Hard cleaned through root.

A source can already be reserved before blocked target is unblocked. Reconsideration now uses allow_unissued_source_rebind in a new frozen source operation after the prior outcome is confirmed. Any open physical task on that actual source UID/cell, including another owner, blocks rebind. Root captures source_reservation_before; no quantity change while physical work is issued. Existing unresolved operation/body is retried without edits. Remaining source binding stays in original RT, no intent rotation inside partial effect.

Full multi-target batch regression passed. JSON_ARRAY_T replacement requires explicit overwrite=true, see [[../concepts/oracle_json_array_semantics]]. Target-selection reasons/candidate samples are recorded in resolved plan; no eligibility bypass is introduced. Marked indivisibility/other physical split modes and independent races remain open.

SQL6dzx9j6k8tr3j target window0.33ms/44, ordinary source2mgfy8y302xw92.23ms/26; bounded201 candidate window/key lookups retained, no additional index. Global metadata CONFIG X for source intent is an existing scalability limit: inventory/NI08 owns a scoped intent-lock proposal; do not remove ordered locks without replacing its race protection.
