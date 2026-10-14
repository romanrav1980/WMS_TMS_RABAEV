# Qwen: ticket092
На собственной исходной обычной приёмке проверить Supply Chain approval, точные BASE qty и направления REUSE/SUPPLIER/DISPOSAL.
Источник: wiki/database/retailcase_ni062_return_approval_20261010.md.
scripts/ni062_return_approval_case.py и concurrency_case.py уже использовали указанные исходники; не повторять их на исчерпанном лимите.

Проверить отсутствие права, неполную коробку REUSE, missing/excess вместо accepted, несуществующую строку, маркированный состав, дробную недопустимую BASE quantity. Совокупные разрешения ≤ accepted. Конкурентные разрешения не превышают исходный лимит; проигравшая операция не оставляет outbox. Exact ID/body replay и conflict.

Сверить immutable original source, append guard, quantity events0, P/H неизменные и один outbox у каждого результата. UI unknown retry сохраняет исходное тело/ID, actor change не раскрывает прежнее досье. sap_verified=false, разрешение не выдаётся за фактическую приёмку склада. После meaningful case записать slow SQL decision.
