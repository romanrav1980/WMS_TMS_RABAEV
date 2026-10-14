# NI07.2: совместный осмотр грузовой зоны

Checkpoint692–694 prepared. Требование12: начальник склада и диспетчер проверяют ворота/линии и подтверждают освобождение зоны. Создаётся append-only журнал заявлений, связанный с прежним RRL_DAY_REVIEW; снимок сверки и quantity executor не меняются.

WAREHOUSE_CHIEF требует отдельное warehouse_day_inspect; DISPATCHER — transport_dispatch_edit. Оба требуют текущий actor/WARE; GLOBAL_ADMIN сохраняет wildcard, но один username не может подписать обе роли. UNIQUE(review,role), UNIQUE operation, сохранённый canonical body/hash/result. Replay проверяет текущую роль/WARE до выдачи старого результата; иное тело прежнего operation отвергается.

Новая подпись разрешена только для последней версии сверки и повторно прочитанного unchanged material hash. Запись — короткая Oracle транзакция с прежним shared RELEASE/CONFIG и ROW warehouse/day/region, общим с DayReviewAPI; независимые дни/склады не получают глобальный CONFIG X. Report capture отдельно от append; источник проверен на source_checked_at, склад после чтения не объявляется неизменным.

observed_empty — заявление оператора. Два разных пользователя и два заявления EMPTY подтверждают осмотр лишь для frozen review, и лишь если captured shipping_register.shipping_zone_empty_confirmed=true. UNKNOWN/неполная topology/занятые ячейки не превращаются в подтверждённую пустоту. Это не закрытие дня: day_closed=false, external_obligations_closed=false, stock_changed=false.

Новая мета-таблица/пакет/guard, не второй stock engine и не блокировка товарного периода. До apply — live отсутствие объектов/permission и source SHA в checkpoint694; paired rollback отказывается удалять непустую историю. Source [migration](../../db/migrations/2026-10-12_ni072_shipping_inspection/002_api.sql). Application/VALID/actual role pair/UI ещё ожидают.

## Результат checkpoint700

Native695/696/699 применены в RABAEV: USER_ERRORS=[] и INVALID=[]. Исправлены legacy-колонки RIGHTS (RIGHT1 — имя права до30 символов; ID — число) и разбор timezone ISO в Oracle. Новое право warehouse_day_inspect. Реальный case698: две разные учётные записи, две роли; точный повтор и resolve вернули исходный результат. Изменённое тело, второе заявление той же роли, самоподписание обеих ролей и неверный hash отвергнуты. Историю нельзя удалить прямым DML. Контрольный P20/H20 сохранён. Временная учётная запись выведена из использования, история оставлена.

Форма подключена к существующей истории сверок: отдельное заявление EMPTY/NON_EMPTY, неизменяемый локальный intent, повтор и запрос исхода. Node syntax проверен; полноценное браузерное принятие и физический осмотр склада остаются открыты. Это заявления к снимку, а не закрытие дня или доказательство пустоты незарегистрированных зон.

SQL по новому журналу: адресные lookup/role-check 0.343–1.124мс, 2.2–5.3 buffers; максимум первого выполнения 38.956мс/148 buffers. Решение: сохранить PK/UQ и ограниченные запросы; глобальные индексы и массовые проверки не добавлять. При промышленном объёме владелец finance проверяет план общего чтения сверки.

## Восстановление739–740

Malformed локальная подпись блокирует POST. Оператор выбирает сохранённую сверку, архивирует raw и перечитывает доступные ему подписи с сервера. Архивирование/чтение/неизменность raw обязательны до очистки; смена actor/API/epoch и другая вкладка сохраняют защиту. JSON восстанавливается только с шестью точными полями, ограниченными operation/review/note и корректными ролью/bool/hash. Форма сохраняет original ID/body для retry/resolve и не превращает NOT_RECORDED в автоматическое закрытие дня. JS syntax PASS; browser network-loss/recovery принятие открыто.
