# Публикация пакета NIKORA WMS/TMS

Дата: 16.09.2026 · версия 1.0.

[Папка Google Drive — Demands to WMS and TMS](https://drive.google.com/drive/folders/12DME2KqiQLmjUAZomTL590vVxjtmkEtb).

Локальный каталог: C:/projects/TMS/wiki/requirements/nikora_retail_selection/.

## Облачные копии

| Локальный MD | Google Drive | Размер, байт |
|---|---|---:|
| [evaluation_method.md](evaluation_method.md) | [Открыть](https://drive.google.com/file/d/1sxYoYsUMyi7QFzhcyrHvlNptjxCgLIIz/view?usp=drivesdk) | 11917 |
| [README.md](README.md) | [Открыть](https://drive.google.com/file/d/1TEEQnEhiqkgvOq1A3zk0ciNmEp7uIKTe/view?usp=drivesdk) | 7021 |
| [functional_requirements.md](functional_requirements.md) | [Открыть](https://drive.google.com/file/d/1o1RycbIq0w1UpP3i-fbr1c4Hu6BoRVrD/view?usp=drivesdk) | 34469 |
| [architecture_and_processes.md](architecture_and_processes.md) | [Открыть](https://drive.google.com/file/d/1Z7DZVuxNRCdZCzKhWOKJ6hvt82d98kXD/view?usp=drivesdk) | 27457 |
| [questionnaire_wms.md](questionnaire_wms.md) | [Открыть](https://drive.google.com/file/d/1FBQslc6oiutShMhXOkiJ-j4a13z33G0M/view?usp=drivesdk) | 25779 |
| [questionnaire_tms.md](questionnaire_tms.md) | [Открыть](https://drive.google.com/file/d/1UK0_rUSY-qiJAHKIA-eGqc7WYY1lYLCj/view?usp=drivesdk) | 22050 |
| [vendor_comparison_wms.md](vendor_comparison_wms.md) | [Открыть](https://drive.google.com/file/d/1d87-hB2pKP3iv7jCb5AMQu5scv_qSbSk/view?usp=drivesdk) | 19988 |
| [vendor_comparison_tms.md](vendor_comparison_tms.md) | [Открыть](https://drive.google.com/file/d/1oqImCXYJBO5xGg38bdpzPvZk5Y9SkQ-4/view?usp=drivesdk) | 18481 |
| [acceptance_scenarios.md](acceptance_scenarios.md) | [Открыть](https://drive.google.com/file/d/1-CE5uWfTHlEAUVKpBYY-rdDBVgjRu96O/view?usp=drivesdk) | 10471 |
| [current_project_gap.md](current_project_gap.md) | [Открыть](https://drive.google.com/file/d/1wTh0Ta7FP6HW-DPO8fVUhQkkFyj9ctpj/view?usp=drivesdk) | 10848 |
| [sources_and_retail_practices.md](sources_and_retail_practices.md) | [Открыть](https://drive.google.com/file/d/1wiUJ7ME00XY2li7Ch8CIsDQ2dH3jnk-x/view?usp=drivesdk) | 17318 |

Этот файл — двенадцатый MD пакета, публикуется в ту же папку. Самоссылка не нужна: он доступен из списка файлов папки.

## Выполненные проверки

- WMS: 48 уникальных вопросов, сумма весов 100%; TMS: 40 вопросов, сумма весов 100%.
- Матрицы: 48×9 = 432 WMS-клетки и 40×9 = 360 TMS-клеток; все строки заполнены статусом П/Ч/НД, источники положительных/частичных утверждений определены.
- Проверены относительные ссылки локального пакета и структура колонок сравнительных таблиц; служебных разделителей не осталось.
- Обязательный scripts/check-encoding.ps1 прошёл: UTF-8, распространённых mojibake-маркеров не найдено.
- Повторно прочитаны метаданные всех 11 основных облачных файлов: совпадают имена, MIME text/markdown, размеры и целевая parent-папка.
- Основной functional_requirements.md повторно прочитан из Google Drive: полный текст совпадает с локальным после нормализации переводов строк/концевого пробела.
- Облачный коннектор не вернул запрошенный md5Checksum, поэтому проверка всех файлов не называется криптографической сверкой байтов.

Статусы функциональности вендоров не подтверждались испытаниями: это исследовательский RFP и предварительное заполнение, а не акт внедрения. Автоматическая проверка документов не означает, что пройдены D01–D12.

## Что не менялось

Продуктовый код, Oracle, существующие sprint-планы и чужие изменения рабочего дерева сохранены. Новых прав доступа/публичных ссылок не назначалось; файлы помещены в указанную пользователем папку. Git commit/push не выполнялись. Исходные документы NIKORA на Drive не редактировались.
