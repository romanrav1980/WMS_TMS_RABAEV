# Ключи справочника складов

15.10.2026. Прямое решение владельца: закрепить уникальный ключ склада; название
склада также является бизнес-ключом. Migration ID: `2026-10-15-wares-identity-keys`.

## Проверенное исходное состояние

В dev RABAEV/orcl `RRL_WARES` содержит291 строку. `ID` и `NAME` заполнены и уникальны;
дубли отсутствуют и по точному названию, и по `upper(trim(NAME))`. До миграции нет
PK/UK; ID допускает NULL, есть только положительный CHECK. Это данные текущего
среза, а не уже существующее Oracle-ограничение.

[Исходные ограничения](../../reports/retailcase/2026-10-15/wares-identity-key/before.json),
[проверка названий](../../reports/retailcase/2026-10-15/wares-identity-key/name-audit.json).

## Решение

- `RRL_WARES_PK(ID)` — первичный ключ для существующих числовых WARE_ID связей.
- `RRL_WARES_NAME_NN` и `RRL_WARES_NAME_UK(NAME)` — обязательное уникальное название.
- Значения не удаляются, не объединяются и не переименовываются. Уникальность NAME
  использует существующее сравнение Oracle; регистр/пробелы автоматически не меняются.
- Учёт времени использует обычные FK на ID после проверки ключа. Подготовленный
  вариант с заменой FK на CHECK не применяется после уточнения владельца.

Статус: APPLIED. [Комплект миграции](../../db/migrations/2026-10-15_wares_identity_keys/manifest.json)
независимо просмотрен; root apply7statements/0errors. [Проверка после применения](../../reports/retailcase/2026-10-15/wares-identity-key/independent-readback.json):
оба ключа и уникальные индексы VALID/ENABLED/VALIDATED, ID/NAME NOT NULL,
все291 пары ID/NAME сохранены. Четыре caller-rollback попытки duplicateID,
duplicateNAME,NULLID,NULLNAME отклонены ожидаемыми Oracle00001/01407.
Товарных изменений нет; глобальный INVALID0. На ID уже ссылаются4 FK actual-time.

## Восстановление

Oracle DDL фиксирует каждый шаг. При частичном применении сохранить исходный
manifest/логи и прочитать точный установленный набор; отдельный reviewed forward
script выполняет только недостающие DDL. Не повторять apply целиком. Полный paired
rollback проверяет ключи и запрещён при зависимых FK; CASCADE не используется.

Связи: [[oracle_change_protocol]], [[retailcase_picker_actual_time_source_20261015]].
