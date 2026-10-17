# Локальный программный выпуск17.10.2026

Проверенный поток: role-only BOX24+EA1 → перемещение → ручной QC → погрузка → выезд → прибытие в окно → полная приёмка магазином25EA. CASE1154, рейс33659, склад P0/H0. Исправлена одна дополнительная legacy-only проверка MOVE через существующий native CASE scope; replay/changed409/foreign403/revoke403 PASS.

KPI V2: целые коробки и отдельные штуки, строка последнему фактическому комплектовщику при согласованной недостаче, возврат сохраняет выработку отдельно от качества. CASE1153:24EA/недостача1/возврат24EA/четыре rates; exact PICK replay после перезапуска сохранил ответ/P25H0. Покрытие наблюдаемых отборов не объявлено полным табелем.

Root проверил реальные compiled scoped KPI и STORE-only вход/акт1440/390px. Акт содержит24+1 по партиям; подтверждён реальным API до read-only UI-прогона. Claude C0124/C0125 RELEASE: блокеров нет. Его скан/вес/recovery регрессии — fixtures, root STORE акт — реальный. Реальные весы/камера этим не проверены.

Oracle53sources/17frozenkits/APPLIED/ERROR0/INVALID0. Quality1151files/0cycles/debt72/24tooling/обаTS PASS; оба production builds и controlled restart PASS. Pytest cache warning не является падением теста.70HTTP/70Oracle+local audit pairs,16SQL log entries/12top/28решений; maxSQL945ms/maxHTTP1020ms — не p95 и не нагрузочный норматив. Решения: bounded WARE/31day/5000fact cohort, set-based JSON_TABLE, без permission cache; планы/статистика при пилотном объёме.

Возвращённой CASE1153 отменены волна/план/неотгруженная тара; доставленная волна594 завершена. Отправленная тара/custody сохраняется.6TEST users/3assignments/3roles/2resources/2devices отключены; stock/history сохранены. Не повторять фабрики и записанные команды без проверки квитанций.

Запуск product.bat; рабочие места http://127.0.0.1:3000/ ; магазин http://127.0.0.1:3010/store/ ; API http://127.0.0.1:8088/docs . Инструкция wiki/runbooks/retailcase_local_product_20261017.md. Время, hashes, кодировка и доказательства — report.json/source-freeze.json, product-flow/, kpi-v2/, claude/C0125/.

Это локальный программный выпуск, не промышленный cutover. Ручной вес работает, электронные API сохранены. Реальный аппаратный пилот OPC40200/сканер/телефон, промышленная нагрузка, Oracle backup restore с RPO/RTO и переключение legacy — отдельный этап. Multi-store выдача частей паллеты отменена; вложенные места одному получателю сохраняются. GitHub не обновлялся. Ponytail/YAGNI действует для всех агентов.
