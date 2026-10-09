# NS00 fixture SQL

Эти файлы задают SQL-шаблоны ядра DS-BASE в существующей RABAEV. Это данные для выделенного dev-стенда, не структурная миграция и не имитация производственной SAP-приёмки.

Запуск из корня репозитория:

```powershell
python -m tools.nicora_environment seed
python -m tools.nicora_environment verify
python -m tools.nicora_environment reset
python -m tools.nicora_environment cleanup
```

Выполнять шаблоны отдельно от runner нельзя: он сначала подтверждает target, владение exact keys, отсутствие внешних ссылок и сохранность внешнего запаса. Commit один на весь набор. `cleanup` убирает только 22 owned строки; существующие warehouse data не перестраиваются. Для восстановления тестового набора после cleanup выполнить seed.

Полное описание — [database mirror](../../../wiki/database/nicora_ns00_fixture.md), provenance и результаты — runtime/test-evidence/nicora_ns00. SQL исполнен в живом Oracle через python-oracledb; OracleApply используется для штатных verification профилей. DDL и migration ledger не менялись.
