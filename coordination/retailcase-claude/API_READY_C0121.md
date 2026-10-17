# API_READY C0121 — CASE handoff UI, не multi-store

READY16.10.2026. Владелец отменил multi-store handover. Работать вместе через прежний канал; ориентир завершения17.10 до08:00 MSK. Два оставшихся пакета Claude сохраняем: этот UI и финальный сквозной прогон. Не запускать старые C0119/C0120 или создание UI поддеревьев.

## Задача

Доведи существующую передачу CASE между комплектовщиками: `wiki-raw/wms_admin_ui_reference/case-handoff.js` сейчас использует последовательные prompt и unsafe удаление сохранённой команды при403/409. Сделай компактную доступную форму/dialog в стиле существующего ARM, с понятными полями ресурса/активной сессии, сканом «Идентификатор паллеты», исходным владельцем/сессией и подтверждением физической передачи. На390px без перекрытий; действия с tooltip и статической URL-справкой. Возврат сохраняет склад/задание. Не обещать автоматический выбор чужой сессии, если API такого списка не отдаёт: числовой ввод остаётся явно подписанным до проверки сервером. Не менять UI Ганта/KPI заново.

Проверь соседние gates в CASE ARM: роли по областям не должны отсекаться только отсутствием legacy плоской группы. Учитывать реальные текущие UI auth.permissions; сервер остаётся authoritative. При передаче чужой области показывать отказ, не заменять его пустыми/старыми данными. Точный повтор неизвестного результата остаётся под прежним ключом и телом; запрещено очищать ранее неизвестную команду только потому, что повтор получил403/409. Новый intent допустим после доказанного исхода/явного безопасного разрешения, а не молчаливого удаления. Повреждённый localStorage не затирать. В RESULT явно отделить состояние старых legacy intents от вновь созданных.

## Готовый контракт

GET `/api/case-pick/tasks/{id}` — существующая карточка (обычная роль должна иметь scoped view). POST `/api/case-pick/tasks/{id}/transfer` теперь допускает authenticated user; native повторно проверяет manager permission по фактическому складу перед новым эффектом и cached replay. Тело:

```
{to_resource_id: number, to_resource_session_id: number,
 to_equipment_id?: number|null, reason: string,
 offline_event_id: string, scan_container: string,
 expected_content_version: number, expected_assigned_to: string,
 expected_from_session_id: number|null}
```

actor задаёт сервер, не клиент. `offline_event_id` неизменен при повторе; тело сохраняется до отправки. Ответ200 `{case_pick_task_id,status:"TRANSFERRED"}`.403 — текущий scope/целевой исполнитель недоступен,409 — physical scan/version/owner/session/content conflict. После timeout/5xx/потери ответа сохранять исходное тело. Непустой груз требует скана, исходного владельца/сессии и версии. Веса/количества этот metadata action не меняет.

Native gate APPLIED: migration `2026-10-16-case-transfer-scope`, readback4SHA/ERROR0/INVALID0. Свежая CASE1151/WARE20902283:24EA,11 actual HTTP WARE/GROUP/revoke/foreign/target-no-permission/replay/conflict, caller rollback+REV PASS. Это изолированный TEST, без оборудования. Evidence `reports/retailcase/2026-10-16/case-transfer-scope/acceptance.json`; текущее состояние может измениться при root cleanup — не выполнять бизнес-команды по этому заданию. Для UI позитивные ответы через fixture честно обозначить, live GET/login безопасны. Admin local development auth — существующая RUSERS учётная запись; не записывать credentials в отчёты.

## Ownership и результат

Claude: case-handoff.js, необходимые CASE ARM HTML/JS/CSS и статическая CASE help. Перед правкой один ACK с точным списком; другие каталоги только сообщением с обоснованием. Codex: весь backend/Oracle, loading/finance/KPI и тестовые stock факты — не менять. Отдельные функции/файлы вместо роста монолита; архитектурный baseline не расширять. Не редактировать TASK/ROOT ready, не публиковать GitHub или статьи через API.

Проверки: JS syntax/encoding,390px и keyboard, fresh submit/exact retry, unknown→403/409 сохраняет intent, corrupt journal, подтверждённый успех очищает только свой intent. Не выполнять неразрешённые физические операции. Итог одним `RESULT_C0121.md`/RELEASE с фактами и ограничениями, чтобы root мог интегрировать без нового запроса. После него root выдаст `RELEASE_READY_C0122.md` для оставшегося финального прогона.
