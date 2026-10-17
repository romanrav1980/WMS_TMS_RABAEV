# CASE work: отдельное рабочее место комплектовщика

15.10.2026. [[../database/retailcase_case_resource_commands_20261015]], [[../runbooks/retailcase_case_work_terminal]]. UI реализован внутренним Codex collaborator; реальный Claude Code выполнил независимое статическое ревью C0113 после18:00. Исправление JournalPanel интегрировано и отдельно проверено root. Полный смешанный складской/аппаратный сценарий этим не закрывается.

## Entry и сценарий

`/case-work/?task_id=<id>` — отдельный React entry с терминальным Basic login, памятью пароля только в странице и локальной опубликованной справкой. Это отдельный экран CLAIM/START, не заявление об установочном PWA/полном scoped UI всех видов отбора. Production mount появляется при существовании dist/case-work/index.html; build обслуживается API8088. Для crypto/Web Locks нужны поддерживающий браузер и secure context (localhost либо HTTPS).

Показываются актуальные CASE/оператор/состояние, собственные активные сессии текущего склада по названиям, отдельное принятие и старт. Старт не проводит товар. Чужое назначение не предлагает START. Время начала берётся из исходного aware server instant, показывается как время устройства; неподтверждённая зона смены спрятана в диагностику. Названия ресурсов не требуют ручного ввода технических ID.

Переход `/wms-admin/case-pick-tsd.html?case_task_id=` существует, но требует отдельного legacy допуска/авторизации. `/assembly/` также не становится role-only из-за успешного CLAIM/START. Это ограничение явно видно у переходов. Паллетный идентификатор не подменяется номером задания.

## Восстановление

Журнал `wms.case-work.journal.v1` сохраняет до первого POST точные URL/compact sorted UTF8 DTO/uppercase SHA256/operation_id/actor/task/server. Пароля в журнале нет. Web Locks сериализует сотрудничающие вкладки. Повреждение/ошибка чтения/записи блокирует новую команду; другая учётная запись или сервер не заменяют исходную операцию.

На mount/reload выполняется только чтение исходного результата.404 означает неизвестный исход. Явный «Повторить исходный запрос» сначала читает квитанцию; только404 допускает POST тех же байтов и operation_id.403/raw409/503/timeout/malformed/hash/чужое назначение в ACK не разрешают исход. Подтверждённый REJECTED409 обрабатывается как top-level квитанция, не как произвольная ошибка detail.

APPLIED сверяет исходные operation/action/actor/task/hash и фактическое назначение, состояние и assignment version expected+changed. Для START обязателен исходный aware instant. Только подходящий окончательный ACK архивируется, после чего удаляется pending и обновляется актуальный контекст. Исправленная команда создаётся отдельным нажатием; автоматического нового operation_id после таймаута нет. Epoch/abort guards исключают применение позднего результата к другому входу/заданию.

Короткие русские объяснения отказа показаны в основной области, точный код/ORA — в свёрнутой диагностике. Все действия имеют title/data-help-id. Длинное имя оператора ограничено двумя строками с полным title. Статья case-work опубликована в локальной базе, редакция3, две связанные инструкции.

## Проверки

- 25 независимых rendered mocked cases: CLAIM360/390/1440, START, строгие ACK, отказ и неизвестный исход, reload/GET404/exact retry, две вкладки, чужой actor/server/task, порча и отказ storage, Unicode и понятные причины сессии, архивный ACK другого задания и повтор исходной команды при503 чтения текущего контекста.
- Production native read под role-only CRES15.OP на CASE1138:360/390/1440, исходный момент старта, текущий статус, существующий raw link и helpv3/two related links. Бизнес-POST блокировались тестом; товарных изменений не было.
- Полный gate1059files/0cycles/debt72+24tooling+обаTS PASS; production build PASS. Существующее предупреждение большого terminal bundle не скрывалось.
- SQL18 Oracle/local audit pairs/maxHTTP122ms/ownslow0; native task_context cumulative avg5.013ms. Сохранены CASE PK и current-actor/session predicates/bound20; индекс не добавлен. Resources/platform проверит actor-history plans при нагрузочном пилоте.

Доказательства: [rendered](../../reports/retailcase/2026-10-15/case-work-ui/root-rendered-mocked.json), [production native read](../../reports/retailcase/2026-10-15/case-work-ui/production-native-read.json), [SQL review](../../reports/retailcase/2026-10-15/case-work-ui/sql-review.json). Native CLAIM/START quantity-free acceptance относится к отдельному серверному инкременту, аппаратного пилота эти проверки не заменяют. После review CASE1138 канонически отменён, session55 CLOSED, роль CRES15.CASE.EXEC неактивнаv4, тестовый пользователь удалён штатным CFG owner и все назначения отозваны. Истории сохранены. Суммарный исходный физический остаток24, резерв0; оба UID и происхождение сохранены. [Проверка завершения](../../reports/retailcase/2026-10-15/case-resource-commands/final-retired-verification.json), [отзыв последних назначений](../../reports/retailcase/2026-10-15/case-resource-commands/remaining-grants-retirement.json).

Native abandon/tombstone неизвестного CASE/TASK metadata intent ещё не реализован; неизвестный исход сохраняется до точной квитанции. Повреждение или несоответствие DTO требует диагностики владельцем, а не небезопасного удаления браузерного журнала. Продолжение этого recovery-контракта отмечено в AK03/AK06.
