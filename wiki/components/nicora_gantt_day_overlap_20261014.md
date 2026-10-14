# Ганта: ночные операции

14.10.2026. [Отчёт72](../../reports/nicora/2026-10-13/72-gantt-day-overlap.md).

Existing GET /api/admin/transport/vehicles/gantt сохраняет формат списка. transport/infrastructure/gantt_rows.py включает рейсы даты и пересекающие её плановые/фактические операции, в том числе незавершённый факт. Диапазон суток полуоткрытый, legacy wall-clock dates остаются прежними. Предел20000строк отклоняется явно. Service вынес SQL в owner transport через public, без нового API или нового планирования.

12прежних операций сохранены. SQL35мс/670buffers: индекс сейчас не добавлять, оценить temporal indexes при росте latency. Crossing/boundary/openfact/point проверены read-only Oracle-моделью, реальной подходящей записи вdevнет. UI C0034 вработе.

## Итог14.10.2026

Нативная часть и UI C0034 завершены. Шкала00–24, полные даты, обрезка суток, отдельная карточка с прокруткой и мобильной вёрсткой; одна панель маршрута. Реальный ночной33564 отображается без подмены. Root итоговый gate PASS:778/0/73,24tests,обаTypeScript. [Итог73](../../reports/nicora/2026-10-13/73-current-sprint-code-completion.md).
