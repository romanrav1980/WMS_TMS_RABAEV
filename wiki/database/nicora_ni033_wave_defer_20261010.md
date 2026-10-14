# NI03.3: завершение возвращённой волны

Ticket169, в реализации. Используется прежняя WAVE_EXECUTION_FINISH через единого stock owner, новая metadata.disposition RETURNED_TO_PLANNING + обязательная reason. Решение не подтверждает исполнение заказа и не меняет запас.

Допуск: исходная волна LAUNCHED,1–200 полностью CANCELLED заданий отбора; CASE CANCELLED без состава/отгрузки; складские задания terminal, DONE допустим только для пополнения; пополнение terminal; активный HARD отсутствует; оригинальный заказ/строки сохраняют OPEN/планируемое состояние/тот же склад; текущего физического исполнения исходных заказов нет. Историческое количество не обнуляется.

Native проверка текущего active RUSERS/WARE/прав выполняется до immutable replay и после ресурсов. Обычный finish требует pick_wave_launch; defer дополнительно pick_wave_cancel. Компиляция привязывает snapshot и исходные строки заказа/плана/fulfillment к стандартным упорядоченным ресурсным блокировкам; исполнение повторно проверяет snapshot. Это узкий путь для полностью возвращённой волны, не частичное смешанное закрытие.

Миграция2026-10-10-169-wave-deferred-demand: saved live root/finish, additive RRL_WAVE_EXEC_ACCESS, paired source rollback/no database copy. SQL db/migrations/2026-10-10_ni033_wave_defer. Применение/результаты ещё не подтверждены.

Реализовано/API/UI и APPLIED в dev: 6 package/body VALID, USER_ERRORS empty, ledgerAPPLIED. Новый режим сохраняется в прежнем immutable operation; metadata reason API1–1000; null mode сохраняет прежний контракт. Экран показывает отдельное явное действие/причину, сохраняет OP до отправки и повторяет тот же запрос. Обычное завершение/ready не ослаблены.

Авторские случаи PASS: native prepare/execute на401 без commit → rollback вернул LAUNCHED и удалил непроведённую OP; свежие concurrentHTTP401 создали одну durable decision с одинаковыми ответами; changedbody409/missingreason422/open395409; текущий foreignWARE20882 перед replay, восстановленный admin получил точный прежний receipt. CASE1036/1037 остаются CANCELLED с историческим1; оригинальный заказ1928/pool остаётся quantity1/picked0/hard0, P20H20 неизменен. При первом авторском вызове использована commit-owning RRL_STOCK_NATIVE_API вместо транзакционного prepare/execute: own402 был корректно committed под OP WAVE.DEFER169:402.ROLLBACK. Это ошибка сценария проверки отката, не заявленная rollback-проверка; история сохранена. Реальная проверка отката выполнена на401, будущий повтор сценария использует оставшийся own400.

При apply выявлен reserved PL/SQL MODE; переименован v_disposition, повторно скомпилирован, USER_ERRORS clean. Исходный checkpoint сохранён, итоговые hashes installed_sources.json. Current manifest/bundle updated/generated only, full bundle не применялся.

SQL: deferred wrapper firstparse70.433ms vs bound cursor5.947ms/4, demand6fw05sc8ct2js1.516ms/15, resource enumeration2.091ms/5, CASE checks0.407ms/15. Решение: сохранить wave/plan PK-bound queries/200 demands/1200items, без нового индекса; coldparse не считать нагрузочным результатом. Owner inventory, large cardinality/partial mixed-wave reconciliation остаются в NI03.3. Architecture535/0cycles/76debt PASS, JS syntaxPASS. Независимая Qwen не запускалась.
