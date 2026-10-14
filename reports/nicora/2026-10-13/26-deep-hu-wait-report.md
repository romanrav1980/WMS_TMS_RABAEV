# 26 · Матрёшка и товар уже в ожидании

13.10.2026, продолжение NI07.2/NI04.1.

## Функциональный результат
Тот же существующий товар20EA упакован в пустую внешнюю паллету HU1069:4bb85f1f15. Дерево: внешнийPALLET → исходныйROLL_CAGE → дваCASE12+8 → исходные2партии. Новый товар/марки/заказ не создавались. ПрежниеHU_CREATE/ATTACH/PLAN_MOVE/TASK_COMPLETE переиспользованы. CASE parent-chain правильно достигает внешнегоRoot, одноTOP не считается как два машиноместа.

После штатного размещения на контроль создано одно задание1152 для возврата всегоTOP вQW. DONE1HU/SYNCED, journal2lots20EA, P20/H20; CTFF1131=14/14,1132=9/9; внешнийRoot3/внутренний12. Exactplan/move replay подтверждены. Это адресный native dev-case с заданными сканами, не реальное оборудование.

## Конкуренция
Отдельная сессия держала только строку собственного TT33635 FOR UPDATE без изменения данных. Новый план получил retryable20840 за0.191секунды, не создал WAIT_RUN/WHT и не изменил20/20. После освобождения строки тот же operation/request штатно создал план и исполнился. Подтверждены нужный ресурс/NOWAIT и атомарность данного отказа; это не доказательство отсутствия всех возможных deadlocks.

## Уже находится в ожидании
Новое обращение после фактического прибытия возвращает tasks[]/already_waiting[TOP], сохраняет immutable metadata receipt и точный repeat. Задания/stock-operation/версии не создаются и не меняются. Под metadata exclusive fence дополнительно запрещено использовать ID посторонней уже проведённой команды HU_CREATE/stock; actualcollision409/noWAIT_RUN подтверждён.

Native1072/HTTP1073: текущий deepTOP, DONE1152/SYNCED, no-move exactcached result — PASS. Перед перезапуском API один повтор вернул503 без захваченного nativecode; после штатногоrootserv.bat тот же сохранённый запрос прошёл. Причину503 не объявляем установленной; owner platform должен сохранять nativecode для подобных неизвестных отказов. Две неверные GET-попытки composition в авторском HTTPскрипте исправлены на наблюдаемый /composition; эти попытки не PASS/не складские операции.

Скриншот32 показывает реальное дерево/2партии/12+8/H12+8/ячейкуQW. Calculatedgrossunknown отображается как отсутствующий; фиктивный вес илиcapacity admission не заявляется.

SQL1072 operation-collision check5.287ms/16buf,2exec. Решение inventory: оставитьOPprimarykey/metadata fence и200treebound; high-leaf/multiTOP профилирование отдельнымticket. Новыйиндекс не требуется на этом свидетельстве.

Gate1067:24 architecture/tooling, обаTS, architecture696/0cycles/76debt PASS. Native after019Errors[]Invalid[]. Последние native extensions не менялиPython/TS; encoding после финальных документов отдельно.

Остаток: несколькоTOP или mixedFULLPAL/CASE однойСТ, slots/capacity waiting target, межскладскаяревизия и полная независимая/внешняя приёмка. Все18 не завершены.
