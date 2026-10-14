# NI03.2 / 635: частичная замена нескольких собственных резервов

Для локальной Qwen; независимый прогон не выполнен. Source: wiki/database/retailcase_ni032_multi_binding_partial_20261012.md, migration631 и native wave source. Исходный case632 уже выполнен и очищен633; не запускать его повторно на прежних фактах.

Создать собственный новый CASE owner12 с двумя HARD6+6 на разных storage UID и существующим target8. Ожидание атомарного перепланирования: target8/H8 + последний storage UID8/H4, первый собственный HARD освобождён, чужой owner8 сохранён. P неизменён. RT указывает на один целый остаточный physical source; actual movement выполняется обычным TASK_COMPLETE, не rebind.

Проверить: target не покрывает все предыдущие bindings, последняя binding не уменьшается, несколько remaining physical sources, недостаточная target capacity, уже выданное физическое задание на любом старом UID, foreign owner/customer/WARE, stale stock/reservation version, нецелая маркированная единица. Отказ не должен менять P/H/units/domain/outbox. Для FULL_PALLET разрешён только один remaining source; HALF не объявлен реализованным.

Конкуренция за same target и late failure: один корректный outcome, rollback целого собственного эффекта; точный original operation replay возвращает сохранённый результат. Отдельно bindings на одном UID/cell: predicted STOCK_VERSION должен учитывать каждую release. Не создавать второй task engine. Cleanup только own fixture через existing core, оставить journal. SlowSQL bounded window200/201 и source reservation lookup.
