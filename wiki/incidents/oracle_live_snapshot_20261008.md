# Oracle VM: зависание после live snapshot

08.10.2026. Только существующая Oracle DB Developer VM, GUID a87bd87f-4d94-4879-a965-afd4e22508f9. Host VirtualBox 7.1.10, VM RAM 16384 MB.

## Наблюдение

После выдачи трёх SYS grants создан live snapshot stock-core-before-runtime-20261008 (d5bede46-4dc9-446a-b9bb-e655e9764315). Во время медленного live сохранения был вызван pause. Снимок завершился успешно, но состояние IConsole стало Running при внутреннем VMM состоянии SUSPENDED_EXT_LS. Гостевая система перестала исполняться; Oracle pool выдавал DPY-4005.

VBox.log содержит SSM Successfully saved и затем ошибки VERR_VM_INVALID_VM_STATE для pause, resume, reset и poweroff. Наблюдается связь с pause во время live snapshot; отдельная причинная проверка не проводилась.

## Восстановление

Обычные resume/reset/poweroff не восстановили выполнение. После этих отказов остановлены только VirtualBoxVM.exe процессы с точным Oracle VM GUID и проверенным executable path. VBoxManage poweroff завершился VM session aborted. Та же VM запущена headless, без restore/discard текущего диска, без клона и без второго Oracle.

На момент перезапуска установка stock runtime ещё не началась: installer отказал при получении connection до первого DDL. SYS grants до снимка подтверждены Oracle metadata. После загрузки подтверждены CDB OPEN/ACTIVE, ORCL READ WRITE, RABAEV host connection и сохранённые grants. Installer завершился: runtime 016 APPLIED, 18 package objects VALID, PREPARED, новых операций 0.

## Решение

Не вызывать pause в ходе live snapshot этого стенда. Для следующего широкого cutover выбрать контрольную точку при заранее согласованной остановке или корректный offline snapshot; не повторять live эксперимент на функциональном шаге. Snapshot этой сессии сохранён, восстановление из него не тестировалось.

[Checkpoint](../../runtime/stock_posting_20261008/admin-grants-and-snapshot.json) · [[../runbooks/nicora_oracle_local_admin]] · [[../database/nicora_stock_posting_implementation]]
