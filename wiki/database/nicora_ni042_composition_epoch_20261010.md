# NI04.2 / NI05.1 — неизменяемая история версии товарного состава
10.10.2026. Миграция073 APPLIED в RABAEV/orcl. Владелец inventory; authoritative Oracle, единственная транзакция RRL_STOCK_POSTING_API. Это выполненный участок, полные спринты открыты.

## Поведение
RRL_PALLETS.STOCK_COMPOSITION_VERSION растёт один раз за root-команду при изменении общего физического количества UID или состава физических маркированных единиц. Резерв и перенос целого неизменённого UID между ячейками версию сохраняют. Обнуление и восстановление количества разными командами не возвращают старую версию. Новая паллета CASE начинает с0; клонирование исходного счётчика запрещено.

Снимок до исполнения сохранён в RESOLVED_PLAN_JSON; сравнение и увеличение происходят после предметного исполнения, до invariant/commit. Ограничения:20000 UID и20000 единиц на команду,10000 единиц на UID. Все PP/ST/CASE ресурсы заранее объявлены; actual ST затем CASE блокируются в согласованном порядке. Версия защищена metadata guard, он не изменяет запас.

QC semantic signature v2 включает эту версию. Изменение состава очищает scan/weight/item/mark proof связанных открытых СТ и возвращает закрытый CASE в WAIT_CONTROL, увеличивает CONTENT_VERSION и записывает CONTROL_REVOKED. Это сохраняется даже при восстановлении прежнего количества. Установка v2 делает прежние v1 допуски недействительными: требуется новый контроль.

## Evidence и границы
Авторский ni042_composition_epoch_case: P5/H2/release, исправление6→5, защита прямого изменения, целый перенос/replay сохраняет epoch, own cleanup.
Авторский ni051_composition_epoch_case: самостоятельный CASE12/H12, контроль,13→12, WAIT_CONTROL/две новые версии CASE, старый scan signature отклонён. Остальной CASE pipeline записан в runtime log; независимая приёмка Qwen ещё требуется.

073 нельзя автоматически откатить к координатору без счётчика: это восстановит старые допуски. rollback.sql явно отказывает; восстановление только forward с сохранением counters/history/QC v2. Checkpoints358–362 предназначены для анализа. Количество и журнал не удаляются.

## SQL
Обе стороны bounded Stock-key доступа; PP keyed updates. Дополнительного индекса на меняющийся счётчик не требуется. SQL событий CASE/ST использует существующие привязки; NI08 отвечает за проверку планов на большом объёме и уменьшение QC warehouse-lock serialization. Live slow-SQL evidence анализируется отдельно; нагрузочная приёмка не заявлена.

Источники: [073](../../db/migrations/2026-10-10_ni042_composition_epoch/apply.sql), [[nicora_ni042_physical_epoch_20261010]], [[nicora_ni051_case_control_20261010]].

Live v$sql:871jmpbqk713v epoch keyed UPDATE0.919ms/9 executions; dfnwypahdz7b5 CASE event INSERT0.551ms/29. Catalog migration queries90–204ms are DDL-only. Decision: retain keyed access, no volatile-counter index. All active clone-birth writers (CASE/task/MES/manual partial move) explicitly reset new UID epoch0; checkpoints362–365.
