# Чтение складских заданий и сессий по областям

15.10.2026. Чтение использует RRL_ACCESS_API.allowed по фактическому складу и проверенному владельцу. Legacy USER_GROUP не заменяется и не получает плоскую сумму новых прав. Native execution guards остаются отдельными: просмотр не разрешает assign/start/complete.

- CASE tasks/shorts: ware_id и native case_pick_view применены до limit. Detail — 404 для отсутствующего/чужого. Суммы соседних заданий волны также ограничены native predicate. scope=self — только сохранённый ASSIGNED_TO вошедшего actor до limit; старый mine без resource_id по-прежнему означает неназначенные задания.
- Warehouse tasks list/detail: warehouse_task_view по FROM/TO; межскладская карточка требует обе области, поскольку раскрывает обе стороны. Одна null сторона допустима, обе null скрыты. ware_id отбирает очередь до limit. Семейство progress/domain-sync ещё использует прежний guard и не объявлено scoped-ready.
- Sessions: ware_id, поле WARE_ID, resource_session_view по складу ресурса; SELF — сохранённый OPERATOR_USER_ID. Revision share guard сериализует с изменением назначений. Фильтр до sort/limit.

Live HTTP: [CASE5](../../reports/retailcase/2026-10-15/resource-timeline/case-native.json), [tasks5](../../reports/retailcase/2026-10-15/resource-timeline/warehouse-tasks-native.json), [sessions4](../../reports/retailcase/2026-10-15/resource-timeline/sessions-native.json). Временные пользователи/роли/назначения очищены; задания, сессии, остатки только читались. Положительная SELF-очередь назначенного комплектовщика требует отдельной фикстуры; наличие self-фильтра само по себе её не подтверждает.

Источники: app/modules/resources/infrastructure/case_view_scope.py, case_scoped_reads.py, case_read_model.py, session_reads.py; inventory/infrastructure/task_scoped_view.py, task_view_predicate.py, task_queue_read.py. [[roadmap/retailcase_access_knowledge_plan]], [[architecture/retailcase_resource_gantt_shift_supervisor]].
