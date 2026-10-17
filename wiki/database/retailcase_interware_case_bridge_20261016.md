# CASE внутри межскладской матрёшки: физическое продолжение

Статус DEV_APPLIED, авторская сквозная программная проверка PASS. Codex — backend/Oracle; Claude C0117 RELEASE K-0068 — обзор восстановления недостач, интегрирован отдельно. Основание — [[../concepts/retailcase_nested_hu_consolidation_20261015]] и [[retailcase_ni061_nested_receiving_20261012]].

## Решение

Историческую CASE_PICK_TASK после SHIPPED не переоткрываем и не переносим её волну на другой WARE. Межскладская приёмка создаёт физический CONTAINER в существующем RRL_PALLETS, сохраняющий идентификатор исходной CASE и неизменяемую связь с её отгрузкой. Новый внутренний UID детерминирован по source load/CASE; исходная CASE, carrier-lot, ASM_FINAL, pick/short/count, ST и fulfillment остаются историей. Товарные листья и маркированные единицы не копируются: существующий grouped receipt приходует каждый исходный UID ровно один раз.

Один новый metadata owner RRL_IW_CASE_BRIDGE/RRL_IW_CASE_CARRIER хранит источник и создаёт физическое продолжение только внутри IN_FLIGHT INTERWARE_RECEIVE с точным frozen plan и общими Root locks. Это не второй реестр остатков и не новый picking task. Дальнейшее перемещение/отгрузку контейнера выполняют прежние HU owners. Один source ST может содержать несколько stock leaves: ограничение receipt(OP,ST) меняется на lookup index, PK(OP,stock UID) и точный native архив остаются защитой от двойного прихода.

Приёмка восстанавливает parent→полученный carrier и carrier→исходные leaves в общей транзакции. Старые links остаются закрытыми. Внешний идентификатор сканируется как текущий физический carrier; историческая CASE больше не создаёт неоднозначность. Чтение проверяет WARE текущего carrier до выдачи состава. Историческое задание доступно прежним способом через task API.

## Масса и тара

Сохраняется исходное основание массы, версия и provenance ASM_FINAL, но оно не становится новым SHIPPING_GROSS/разрешением QC. Неизвестная тара в API остаётся UNKNOWN/null; технический default0 HU не является измерением. Владение оборотной тарой не передаётся приходом товара: исходная HELD бронь остаётся закреплённой до штатного TARE_OFFER/TARE_ACCEPT. Связь этой брони с физическим продолжением сохраняется в origin. История и доступность тары не обнуляются и новая бронь не создаётся автоматически.

## Граница и приёмка

Первое межскладское плечо, целое дерево до200 узлов и200 листьев, собственный ST каждой исходной CASE; одна CASE может содержать несколько листьев. Прежний multi-hop guard и запрет частичного nested receipt сохраняются. Дальнейший handover поддерева магазину — отдельный инкремент, не обещание этого комплекта. Обычный CONTAINER/STOCK путь сохраняется.

План: fresh source checkpoint31 объектов/INVALID0; SQL apply/verify/rollback, code checkpoint и запись ledger до live установки. Native guards источника/получателя, caller rollback/commit/replay, missing/duplicate/foreign/stale проверки и SQL review по одному изолированному смешанному сценарию. Исходное MH16 дерево/CASE1140/1142 не отгружать ради теста. Source/history и новые business facts сохранять; rollback отказывается при retained bridge/multi-leaf history. Авторские проверки не являются независимым/аппаратным пилотом.


Миграция `2026-10-16-interware-case-bridge` установлена, frozen SHA `5d86c86404eae1bee88f9f4732ed673fc29c925c6e4d3e4d72e86e95082b4997`:31 исходник before,34 source hashes после, ledger APPLIED/ERROR0/INVALID0. Runtime обнаружил ORA-40573 при SQL-использовании x.get_number; отдельная `2026-10-16-interware-case-json-scalar` (SHA `2558e91144188b04fd91b324e74decd20f694f81192cbde7de0d2a95364980ab`) присваивает NUMBER до SELECT, verified1SHA/INVALID0. Исходный frozen комплект не переписывался. [Миграции](../../db/migrations/2026-10-16_interware_case_bridge/README.md), [scalar fix](../../db/migrations/2026-10-16_interware_case_json_scalar/README.md).

## Фактический сквозной результат

Новый изолированный груз IC16.ce9c011b16: WARE20846272→30846272→магазин, рейсы33651/33652. CASE1145 — ASM_FINAL1EA, CASE1146 — BOX24+EA1, всего3 исходных товарных UID/26EA. Дерево top→2CASE→3leaf принято с caller rollback, commit, точным replay и conflict изменённого тела. Каждый прежний SSCC разрешается в свой новый IW.CASE carrier на целевом WARE. Исходные CASE остаются SHIPPED на исходном складе; ASM и две HELD брони тары сохранены.

Целый HU перемещён складским заданием, custody первого плеча освобождён, подготовлены3 целевых ST, штатно назначены на второй рейс, погружены и отправлены. Магазин принял26EA по PAPER_COUNT; replay не повторяет эффект. Итог заказа ASM:1 отгружено/1 принято, обычного:25/25; unattributed/unreceived0, P/H обоих тестовых складов0. STORE_RECEIPT атомарно освободил custody второго плеча; дополнительная независимая release-команда отказана как уже выполненная. Защищённые WARE6667491/20220394 неизменны. Волны577/578 DONE,3 тестовых пользователя/2 ресурса/прибор отключены, назначения отозваны; истории не удалялись.

Отчёты: [receipt rollback/replay/сканы](../../reports/retailcase/2026-10-16/interware-case/flow/receive-readback.json), [второе плечо](../../reports/retailcase/2026-10-16/interware-case/flow/onward-resume.json), [приёмка и исходные заказы](../../reports/retailcase/2026-10-16/interware-case/flow/store-readback.json), [retirement](../../reports/retailcase/2026-10-16/interware-case/flow/retirement-final.json). Промежуточные отказы и ошибки test harness сохранены. Это авторская проверка на TEST-данных, не физический или независимый пилот; новые scoped write/отзыв/конкуренция всех ролей не объявлены проверенными этим admin-сценарием.

Складской ручной QC и происхождение веса при погрузке выполнены отдельными инкрементами [[retailcase_manual_warehouse_qc_20261016]]/[[retailcase_manual_qc_load_origin_20261016]]. Пустой внешний BOX явно снят командами HU_DETACH перед отгрузкой: native closest-box coverage не допускает двойного независимого учёта внешней коробки и вложенных CASE. Универсальный manifest произвольных коробок и handover части дерева остаются открытыми.

## SQL и ограничения выпуска

[Финальный SQL review](../../reports/retailcase/2026-10-16/interware-case/flow/sql-review-final.json):35 явных Oracle/local HTTP pairs, max1686мс; slow-log56мс policy/126мс source/544мс onward metadata. Native calls не приписаны HTTP. V$SQL — ограниченная cumulative выборка, не p95. Решение: bounded200 и существующие PK/index lookups сохранить; transport/inventory integration owner перед нагрузочным пилотом разделяет время admission/prepare/execute/audit для погрузки1686/1016мс и проверяет план/статистику и N+1 конструкторов ST для544мс onward. Batch — при подтверждении повторных чтений; произвольный новый индекс/кеш и ослабление locks не вводятся.
