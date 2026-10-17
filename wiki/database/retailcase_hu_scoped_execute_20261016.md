# Базовые HU-команды по назначению роли

Статус DEV_APPLIED/5SHA/ERROR0/INVALID0, авторский native/HTTP кейс PASS. Продолжение [[../components/retailcase_hu_scoped_read_20261015]] и блока1 [[../roadmap/retailcase_finish_single_claude_20261015]]. Owner inventory/platform; authoritative native RRL_HU_EXEC_ACCESS и прежние HU/Root owners, HTTP получает identity.

В CREATE/ATTACH/DETACH/MOVE scoped-only пользователь проверяется по фактическому WARE ячейки до rich compile и replay, затем повторно после REV→config/resources locks и в execute. Для child/target проверяются их собственные WARE. Legacy flat/global ветка сохраняется. Неверный/неопределимый источник возвращает403 без состава. Никаких Python-only допусков, нового писателя остатков или выдачи flat прав нет.

Прямое присоединение CASE сохраняет старый отдельный manager guard и пока недоступно scoped-only пользователю. Планирование/выполнение HU-задачи, slot/repack и shipping остаются отдельными контрактами; четыре базовые операции не объявляются всей матрицей прав. Имена полей/проводка/сканы/версии/thermal/история сохраняются.

MIGRATION_ID `2026-10-16-hu-scoped-execute`, frozen SHA `ed1089477064a2e024d8c98c8c9a7e0229b04ff52a5d6cf7e4a92e4373ae7bbd`. Before3 sources/INVALID0, новый read-only helper spec/body, два существующих body. Source guards, code checkpoint HTTP, paired rollback; rollback отказывается при retained scoped HU history. План: новая изолированная WARE/GROUP fixture, positive physical3EA attach/move/detach, foreign/revoke/replay/conflict, caller rollback, REV fence, SQL review. Авторская проверка не независимый пилот.

## Выполненная проверка

Новая fixture HS16.3c390ab3a0/WARE40246672, пользователь с homeWARE1 и flat execute/admin=0. WARE assignment позволил CREATE двух контейнеров и ATTACH3EA→child→parent. Точный CREATE replay PASS, изменённая тара с тем же op409, чужой WARE50246672 CREATE/MOVE403. Отзыв WARE assignment запретил даже прежний CREATE replay. CURRENT GROUP assignment позволил переместить то же дерево; удаление WARE из группы дало DETACH403, восстановление членства — успешный DETACH.

Прямой native MOVE подготовлен под этим scoped пользователем, execute прошёл, затем caller rollback сохранил3EA на прежней ячейке/H0 и не оставил операцию. Пока prepare держал shared REV, второе соединение не получило exclusive REV (ORA54); изменение прав не проходит между повторной проверкой и проводкой. Global admin по прежней ветке создал пустой контейнер. Прежние ошибки fixture pick-cell/IS_SYSTEM сохранены; настройки исправлены только у собственных новых ячеек, бизнес-guards не ослаблены.

Назначения отозваны, роль/группа inactive, пользователь DELETED;3EA и контейнеры сохранены в изолированном тестовом WARE, история не удалялась. [Native/HTTP acceptance](../../reports/retailcase/2026-10-16/hu-scoped-execute/acceptance-v3.json), [retirement/legacy](../../reports/retailcase/2026-10-16/hu-scoped-execute/retirement.json), [source/ledger readback](../../reports/retailcase/2026-10-16/hu-scoped-execute/root-readback.json).

## SQL

[Review](../../reports/retailcase/2026-10-16/hu-scoped-execute/sql-review.json):14 exact Oracle/local pairs, max219мс, own slow0, bounded V$SQL. Решение: сохранить UID/cell lookups, текущие permission checks и REV fence; не кешировать разрешения между отзывами, не добавлять индекс без измерения. Inventory/platform профилирует prepare/execute/audit и планы при повторных500мс SQL/1000мс HTTP на пилоте. Shared cursor averages не считаются p95 данного сценария.
