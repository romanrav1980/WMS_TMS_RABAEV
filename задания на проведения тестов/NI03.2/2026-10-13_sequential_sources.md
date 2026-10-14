# NI03.2 — последовательные источники834–837

Среда RABAEV/orcl. Читать wiki/database/retailcase_ni032_sequential_sources_20261013.md и migration834, не пересоздавать защищённые688/744/773/632/stock20/20.

1. Проверить остатки/резервы на свежем отдельном SKU: target4, own6+6; первая подача целой паллеты, продолжение по собственному HARD, чужой владелец сохраняется.
2. Отказ вместимости до изменения любого резерва; затем валидный повтор новой подтверждённой команды.
3. Отдельный случай без свободного target после первой подачи: реальное второе поступление через прежний REPL_CONTINUATION, без нового writer/раздвоения физического UID.
4. Неизменённая binding сохраняет version; zero release не вызывает reserve release; source stock version совпадает с фактическими положительными releases.
5. Конкурентная выдача physical task и rebind: один согласованный победитель, другой отказ без частичного эффекта. Повтор с прежним operation/body возвращает результат; другой body отклоняется.
6. Проверить две retained bindings одного выбранного UID/cell: текущий ограниченный отказ; не объявлять этот режим поддержанным.
7. Current resourceUI ASSIGNED не позволяет nearest dispatch; confirmed assignment сохраняется после queue refresh/failure; не использовать рабочие/чужие задания для mutation.

Записывать только реальные результаты, ограничения и slowSQL решение. Отчёт в reports/retailcase/2026-10-13. Скриншот браузера не доказывает аппаратный сканер или государственный ACK. Полную приёмку не заявлять по авторскому case835.

Дополнение840–847: воспроизвести один physical FULL_PALLET для shared owners, отсутствие вторичного задания после ARRIVAL, CANCELLED только unissued/remaining0 placeholder, частично покрытый owner остаётся открытым. Проверить global total200 row IDs и currentWARE before UPDATE; positive live846 отдельно от author840. Failed historicalattempts not accepted.
