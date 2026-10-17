# Нативная область запуска волны

15.10.2026. APPLIED 2026-10-15-wave-launch-scope. В существующем WAVE_LAUNCH найден плоский финальный gate RRL_HAS_WRIGHT без привязки к складу волны. Проверка native pick_wave_launch по фактическому WARE_ID добавляется до компиляции плана, после захвата ресурсов и в execute. Revision share guard удерживается до конца команды; хеш/operation_id/количественный writer не заменяются. Legacy RRL_HAS_WRIGHT неизменён.

[Apply](../../db/migrations/2026-10-15_wave_launch_scope/apply.sql), before/rollback/verify/checkpoint рядом. Прямое поручение владельца — роли по областям и выполнение спринтов. Scope изменения ограничен запуском; метаданные продолжения ещё требуют собственных native gates. UI-кнопка запуска не объявлена READY.

Live guard4 PASS: native-only собственный склад, чужая canonical команда запрещена до плана, собственная дошла до WAVE_NO_SOFT_RESERVATIONS, revoke запрещает следующую. Физический положительный запуск не принят: подходящих PREVIEW/SOFT фикстур сейчас нет. Follow-up scoped-command-lock-order сохраняет strict begin_plan и берёт revision guard после него. Перенос не ослабляет no-prewrite invariant. Продолжение запуска по-прежнему отдельный остаток, UI-кнопка не READY.

15.10 follow-up: прежний остаток metadata continuation закрыт APPLIED и bounded DEV native/HTTP proof в [[retailcase_wave_launch_continuation_20261015]]. Исходные guard4 остаются историей этого первого increment; новые positive/recovery/compensation evidence и ограничения находятся в follow-up, без объявления hardware/load готовности.
