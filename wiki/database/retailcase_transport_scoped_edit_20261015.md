# Scoped-редактирование рейса · 15.10.2026

Миграция2026-10-15-transport-scoped-edit, PREPARED. По повторному поручению владельца выполнить принятые AK/KH спринты. [Apply](../../db/migrations/2026-10-15_transport_scoped_edit/apply.sql), [rollback](../../db/migrations/2026-10-15_transport_scoped_edit/rollback.sql), [verify](../../db/migrations/2026-10-15_transport_scoped_edit/verify.sql), checkpoint/точные before bodies рядом. Target RABAEV/orcl, INVALID до0. Checkpoint HEAD+SHA256 сохранён до apply, публикация не выполняется.

RRL_TRANSPORT_PLAN_RULES.assert_actor сохраняет существование фактического склада и ошибку, но допуск transport_dispatch_edit решает RRL_ACCESS_API.allowed по этому WAREHOUSE. Проверка чистая, без новых locks/DML, поэтому read-only preflight остаётся допустимым. RRL_TRANSPORT_EDIT_API.actor_allowed получает shared access revision guard и проверяет наличие реального edit-мандата; update_trip затем сохраняет проверки каждого locked источника/ограничение200/владельца пустого рейса/погруженного груза/замороженного плана/допуска машины. Native правила не дублируются в Python.

Пустой рейс всё ещё не содержит отдельного warehouse поля: создание/редактирование собственного пустого разрешается по текущему складу RUSERS. Это не выдача права на все назначенные РЦ. Создание в произвольно выбранном новом РЦ требует следующего явного контракта источника склада. Legacy RRL_HAS_WRIGHT/USER_GROUP не меняются, массового назначения нет. Подключение API PATCH/create выполняется только после native rollback-only verify. Иные плановые/складские команды не объявляются переведёнными из-за изменения общего helper.

[[architecture/retailcase_scoped_access_and_knowledge]], [[roadmap/retailcase_access_knowledge_plan]].

## Live apply и проверки

APPLIED; target RABAEV/orcl;2package bodies VALID, USER_ERRORS0, INVALID0.9rollback-only native checks PASS: pure assert_actor в READ ONLY, native-only note edit, foreignwaredeny, mixedbothgrants, revoke, emptyownware mandate, ownemptycreate/edit, otherauthoremptydeny, notes+fixtures rollback. POST /tasks и PATCH /tasks/{id} используют identity dependency, финальная политика остаётся native. Автоповтор/новый operation_id контракт этим изменением не вводится; прежние create/PATCH требуют установления исхода при timeout.

Изменённые бизнес-строки не фиксировались; два тестовых sequence ID потреблены и откатились вместе с заголовками. Existingnotes до/после равны; физического движения/финансового признания нет. [Native evidence](../../reports/retailcase/2026-10-15/dispatch-scope/native-edit.json). Rollback подготовлен, не исполнялся; независимая приёмка отдельно.
