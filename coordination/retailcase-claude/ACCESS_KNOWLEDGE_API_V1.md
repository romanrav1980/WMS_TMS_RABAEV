# Access / Knowledge API v1 — координационный контракт

14.10.2026. Codex — backend owner, Claude — UI consumer. Базовая auth пока существующая; бизнес-допуск на сервере/Oracle. Эти API реализуются последовательно: READY отдельно в канале. Чужие области не объединяются с правами другой роли. Объекты и версии — строки/целые в JSON, timestamps ISO8601 timezone. Отсутствующие поля не означают нули.

## Доступ

GET /api/access/me — {username,legacy_group,assignments:[…],access_revision}. Только собственные назначения.
GET /api/access/catalog — {roles:[{role_id,title,permissions:[str],active,version}],scope_kinds:[str],rights:[str]}. Требует access_admin_view; GLOBAL_ADMIN сохраняется.
GET /api/access/groups?query=&limit=50 — [{group_id,title,member_kind,version,active}], max100.
GET /api/access/groups/{id} — {group_id,title,member_kind,version,active,members:[{kind,object_id,title}]}; группа ограничена200 элементами v1.
GET /api/access/objects?kind=WAREHOUSE&query=&limit=50 — [{kind,object_id,title,parent_kind,parent_id,version,active}], max100.
GET /api/access/assignments?username=&limit=50 — [{assignment_id,username,role_id,scope_kind,scope_id,membership,snapshot_version,valid_from,valid_until,revoked_at,assigned_by,reason,version}], max100.
POST /api/access/explain — {permission,object_kind,object_id,username?} → {allowed,reasons:[…],access_revision}. Чужое объяснение требует админского просмотра.
POST /api/access/commands — {operation_id,command_type,payload}. Типы ROLE_SAVE, GROUP_SAVE, OBJECT_SAVE, ASSIGN, REVOKE. Обязательная expected_version в payload для изменения; создание0. Возвращает {operation_id,command_type,object_id,version,replayed:false}. Совпадающий повтор возвращает сохранённый результат; изменённый payload409. ROLE_SAVE {role_id,title,permissions:[str],active,expected_version}; OBJECT_SAVE {kind,object_id,title,parent_kind?,parent_id?,active,expected_version}; GROUP_SAVE {group_id,title,member_kind,members:[{kind,object_id}],active,expected_version}; ASSIGN {assignment_id,username,role_id,scope_kind,scope_id?,membership:CURRENT|SNAPSHOT,snapshot_version?,valid_from,valid_until?,reason,expected_version:0}; REVOKE {assignment_id,reason,expected_version}.
GET /api/access/commands/{operation_id} — свой результат либо просмотр администратором;404 означает только отсутствие видимой зафиксированной квитанции, не разрешение изменить старую команду.

Новые права: access_admin_view/access_role_manage/access_group_manage/access_assign_manage. Настройка состава ролей и глобальных областей — отдельный мандат; role_assign_edit из старого proposal не считать готовой реализацией. Назначающий не может увеличить свой scope/срок/права или обойти ограничения через GROUP_SAVE. GLOBAL_ADMIN имеет прежний особый режим.

## Знания

Существующие GET /api/help/articles?query=&limit=20 и /api/help/articles/{id} сохраняются. Дополнительные поля article допустимы; текущие article_id,title,summary,body,revision,sources,related сохраняются.
GET /api/knowledge/spaces — [{space_id,title,version}].
GET /api/knowledge/articles?space_id=&query=&status=&limit=50 — [{article_id,title,summary,status,version,space_id}], max100; черновики только уполномоченным.
GET /api/knowledge/articles/{id} — {article_id,space_id,title,summary,body,status,version,related:[str],sources:[str],required_permissions:[str],updated_by,updated_at}.
GET /api/knowledge/articles/{id}/history?limit=20 — [{version,status,actor,created_at,reason}], max50.
POST /api/knowledge/commands — {operation_id,command_type,payload}; SPACE_SAVE {space_id,title,expected_version}, ARTICLE_SAVE {article_id,space_id,title,summary,body,related:[str],sources:[str],required_permissions:[str],expected_version,reason}, PUBLISH/ARCHIVE {article_id,expected_version,reason}. ARTICLE_SAVE создаёт/меняет черновик, не заменяет опубликованную редакцию до PUBLISH.
GET /api/knowledge/commands/{id} — квитанция по тому же правилу, что access.
Права knowledge_edit/knowledge_publish/knowledge_admin; читателю только опубликованная разрешённая редакция. Изменение read-permissions и публикация требуют publisher, чтобы editor не расширил доступ к чувствительному тексту. История черновиков читателю не открывается. Body — безопасный текст, без HTML; межстатейные ссылки — стабильные article_id. Опубликованные знания wiki импортируются по curated allowlist, не через произвольный filepath клиента.

Ошибки: 401/403/404/409/422, detail {code,message,outcome_confirmed,operation_id?}; network/5xx не означает подтверждённый отказ. 409 version conflict не разрешает изменить payload под тем же ключом. expected_version меняется только в новой команде после разрешения предыдущего исхода. Конкретный код/контракт уточняется через канал, без молчаливых несовместимых изменений.
