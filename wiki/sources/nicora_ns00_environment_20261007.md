# Источники исполнения NS00 — 7 октября 2026 года

По поручению владельца после первоначального чтения NS01 переключились на NS00. Для NS01 изменений и реестра NK-ID нет. Рабочий scope — существующая RABAEV в выделенном ORCL/orcl, без DDL и новых схем.

Источники требований — [карточка NS00](../requirements/nikora_delivery_v55/execution/sprints/ns00.md), [DS-BASE](../requirements/nikora_delivery_v55/execution/fixtures/base.json), [fixture contract](../database/nicora_ns00_fixture.md). Исходное состояние и прежняя перекомпиляция — db/restore_points/nicora_ns00_20261007 и tmp/nicora_ns00; ранние артефакты не считаются полной Oracle backup.

Фактическое evidence — [runtime report](../../runtime/test-evidence/nicora_ns00/report.json), [паспорт](../../runtime/test-evidence/nicora_ns00/passport.json), [source snapshot](../../runtime/test-evidence/nicora_ns00/ns00-review-source.zip), [source hashes](../../runtime/test-evidence/nicora_ns00/source-manifest.json). Сохранены ошибки первой остановки Uvicorn и offline npm cache miss; последующие replay/restart и fresh online install подтверждены отдельно. Проверки проведены автором, не Claude.

Правила интерпретации: core DS-BASE — 22 строки, не все business settings/Track & Trace. Повтор/очистка/падение транзакции проверены живым Oracle, без SQLite. Cold Oracle reinstall и independent/owner acceptance не выполнены; NS00 остаётся in_progress. UI demo ARM и предупреждения Ant Design не считаются реальным складским evidence. Ссылки в wiki актуальны на этот source hash; после нового изменения проверять новый отчёт.

При финальной проверке исправлена ASCII-подмена русских дополнений при Windows PowerShell pipe в Python. Тексты восстановлены из исходных UTF-8 материалов, поиск повторных вопросительных знаков выполнен отдельно. Исправлена также прежняя повреждённая подпись ссылки nicora_execution_after_tooling в wiki/index.md, по содержанию её страницы; raw sources не менялись.
