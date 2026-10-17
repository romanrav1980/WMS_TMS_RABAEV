# Диспетчер: scoped-чтение рейсов

15.10.2026, AK05. GET tasks/list/detail/STS/operations, vehicles/gantt и tasks/export.xlsx используют текущую RUSERS identity, а допуск — native RRL_ACCESS_API.transport_dispatch_view на склады фактического состава. Фильтр в Oracle до группировки, policy revision shared guard до завершения чтения. В mixed trip доступ нужен ко всем warehouse members, NULLware не разрешается. Emptytrip видит GLOBAL_ADMIN либо его автор с текущим warehouse мандатом. Не flatten role/scopes; RRL_HAS_WRIGHT и существующие группы не менялись.

Exact task_id не зависит от default даты; общий default31д, open-ended диапазон ограничивается31д, предел93д; max2000рейсов/20000операций, превышение явно вместо усечения. Выделение native predicate/filters в transport инфраструктуру уменьшило legacy service; baseline только ужесточён, не расширен. Другие каталоги/команды не объявляются scoped из-за этого инкремента.

8live HTTP/native checks PASS на изолированном новом пользователе с NONE group: назначенный склад, чужие direct/list, полный XLSX, разрешённый Гант, mixedчастичныйdeny/полныйallow/revoke, widewindow422. Existingtrips33641/31050 только читались, metadatafixtures очищены, stockNONE. [Evidence](../../reports/retailcase/2026-10-15/dispatch-scope/http-native.json).9focusedtests (старые datewindow+timeline) PASS.

Обнаружен старый дефект: StreamingResponse(BytesIO) через текущий audit возвращал начальный166byte fragmentXLSX. Для bounded tasks/export.xlsx использован обычный Response с готовымbytes, проверены ZIPCRC/лист/ID33641. Остальные billingexports требуют такого же отдельного кейса; владелецCodex, backlog AK05-EXPORT02 до принятия биллингового места. Это фикс маршрута, общий middleware не изменялся.

Новых slowSQLсобытий по transport за30мин не найдено. Сохранять ограниченный период/выборку; перед изменением индексов проверить nativepredicate plan/buffers на многоскладской нагрузке, ownerCodex AK05-PERF01. Общий gate временно зацепил незавершённые файлы Claude, ошибки переданыC0077/C0081; окончательная приёмка после егоRELEASE. [[database/retailcase_transport_scoped_edit_20261015]], [[architecture/retailcase_resource_gantt_shift_supervisor]].
