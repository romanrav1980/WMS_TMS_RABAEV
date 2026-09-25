# Публикация требований WMS табачных хабов

17 сентября 2026 года. Версия пакета 1.0.

[Отдельная папка Google Drive](https://drive.google.com/drive/folders/1TnH9OjsLttPRFltYlTs3ov19Sx7INLYn) находится внутри ранее согласованной папки Demands to WMS and TMS. Доступ и правила общего доступа не изменялись.

## Актуальный опросник — редакция 2.0, 18 сентября 2026 года

Самостоятельный документ для печати и передачи поставщику: 100 вопросов, 15 предметных областей, веса в сумме 100%, поля ответа, критические условия и методика расчёта внутри. Подволны сборки включены по уточнению пользователя. Веса редакций 1.0 и 2.0 не смешиваются.

| Документ | MD на Диске | Word на Диске |
|---|---|---|
| Опросник поставщика WMS — редакция 2 | [MD](https://drive.google.com/file/d/1B_5Y32d-poYwRVUEBq-26mQX649boEAj/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/13sgQCPFJyKbUt9xc_zkc_hO764BEhlAC/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |

Локальные файлы находятся в supplier_questionnaire_v2. Проверены 100 вопросов, 15 весов областей, общий вес 100%, отсутствие ссылок на другие документы, все 18 печатных страниц Microsoft Word. UTF-8 проверен; после загрузки сверены имена, MIME, размеры и папка, текст MD повторно прочитан и совпал с локальным.

## Основные файлы пакета 1.0 (старый опросник сохранён для истории)

| Документ | MD на Диске | Word на Диске |
|---|---|---|
| Обзор комплекта | [MD](https://drive.google.com/file/d/1pdjzLtMJsOVQ7MLs_QocFr0Es05aJRK8/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1b4cOvPCe_uBrtUlWer3PAKqI7PwSAnLg/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |
| Функциональные требования | [MD](https://drive.google.com/file/d/1elI-fcmrZN9QmIz1toY8uWigKkep4xAa/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1bQtPFPCbRXhQN-UZHQnK011JFxzkQeX6/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |
| Архитектура и интеграция | [MD](https://drive.google.com/file/d/1DQ0fW2ZQ_gpFBpgl0ZouPWJcc2i7wGes/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1NOkvtTxpJLpcyrDZbTk69amrztUFKuQ7/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |
| Опросник WMS | [MD](https://drive.google.com/file/d/1EzCF621VQ6nncmmiFDdTz-Ww_a_PGvOj/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1iR5odGDWugV4ZUJGRpWfps5RH1up624S/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |
| Веса и приёмка | [MD](https://drive.google.com/file/d/1IVU0E54QquW4B6uU2TcZx9HckIFOKiLx/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1OLcc8NCr6ZEZyni_vy5IWUOXS-D8TB_y/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |
| Источники и профиль | [MD](https://drive.google.com/file/d/1Y1FK_Sq5ijDUqLrFidqF2xcG0EPIFC_k/view?usp=drivesdk) | [DOCX](https://docs.google.com/document/d/1r6IjQroagllLrGbj1EkVZEEjOIk6X8w3/edit?usp=drivesdk&ouid=118435630469296112291&rtpof=true&sd=true) |

## Проверка комплекта

- 52 уникальных требования TH-01–TH-52 и 52 соответствующих вопроса; индивидуальные веса во всех документах совпадают, сумма 100%.
- 18 сквозных сценариев приёмки и 20 семейств интеграционных сообщений.
- Шесть основных MD и шесть DOCX; Word-копии визуально проверены на всех 48 страницах.
- Проверены целостность OOXML, повторяемые заголовки таблиц, гиперссылки и отсутствие текста за границами страницы.
- После загрузки проверены имена, MIME, размеры и принадлежность папке всех 12 основных файлов. Полный текст функциональных требований повторно прочитан с Диска и совпал с локальным.
- Проверка UTF-8 scripts/check-encoding.ps1 пройдена.
- Сценарии SAP, Track & Trace и Oracle в рамках подготовки документов не исполнялись; документы не являются сертификатом готовности текущей WMS или вендоров.

## Локальное расположение и воспроизведение

Основные MD находятся в wiki/requirements/tobacco_regional_hubs, Word-копии — в docx этой папки. Относительные ссылки работают в локальном комплекте; для открытия отдельных документов на Google Диске использовать прямые ссылки выше.

Создание: tools/tobacco_hub_wms_export.py. Word-рендер: tools/tobacco_hub_wms_pdf.ps1. Проверки: tools/tobacco_hub_wms_validate.py. Конвейер использует общее оформление tools/retail_standard_export.py, не изменяя прежний retail пакет.

Штатный рендерер навыка документов был вызван и сообщил об отсутствии LibreOffice. Применён локальный Python/Word-конвейер с отдельным невидимым экземпляром Word и просмотром полученных PNG. QA PDF, PNG и журналы лежат в tmp/tobacco-hub-wms-qa и не включены в облачный комплект.

Продуктовый код, Oracle и существующие пользовательские изменения не менялись. Отдельная ветка оформлена как самостоятельный каталог требований, без переключения Git-ветки и без commit/push. Специфичные для страны нормы и протокол внешней Track & Trace уточняются профилем внедрения.
