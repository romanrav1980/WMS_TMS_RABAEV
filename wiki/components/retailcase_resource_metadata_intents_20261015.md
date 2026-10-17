# Отказ от несостоявшегося CASE/TASK назначения

Статус: **PREPARED / NOT APPLIED**,15.10.2026. Owner resources. Native migration и типизированные Python границы подготовлены; root выполняет review/DDL/native fixtures отдельно. Ничего из этого не объявлено активным API или независимой runtime приёмкой.

Таймаут/404 не снимает исходный журнал. Оператор может отдельно запросить прекращение именно сохранённого, ещё не записанного CASE CLAIM/START или ordinary TASK ASSIGN/START. Новый native tombstone выдаёт ABANDONED только при отсутствии любой исходной квитанции под тем же OP/config/task fence и запрещает позднее выполнение исходного operation_id. Ни задание, ни товар, ни факт уже принятой команды этим не отменяются.

Если исходный APPLIED или REJECTED уже записан, он остаётся неизменным. Отдельное чтение resolution возвращает исходную квитанцию; запрос abandonment отказывается RECORDED_READ_REQUIRED. Для неизвестного результата404, отозванного допуска, чужого actor/target или несовместимого журнала нет clear/newop обхода. Только строгая исходная квитанция либо совпадающее native ABANDONED доказательство позволяют UI разрешить ожидание.

Используются прежние canonical command builders и действующие current-authority owners. В два native spec/body добавлены только authority wrapper и late-original guard после oldACK lookup, до effects/REJECTED. DOMAIN+original operation сохраняет глобальную идентичность. Старые receipt enums не расширяются. Original expected version сохраняется рядом с current version at abandon; устаревшая версия сама по себе не мешает доказать отсутствие, текущие права повторяются под locks.

[Подробный контракт, lock order, exact-source checkpoint, rollback criteria и матрица предстоящей native приёмки](../../db/migrations/2026-10-15_resource_metadata_intents/README.md).29 mocked boundary/strict ACK/API checks PASS; это не Oracle/concurrency acceptance. UI/main/public composition не менялись. Unloading START — отдельный будущий owner-bound механизм, не часть этого пакета.
