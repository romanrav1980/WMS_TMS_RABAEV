# NI04.1 / NI07.1: начало физической сборки обычной BOX
Применено516/518, native VALID. 517: empty BOX no clock, first attachment/replay, fully empty/new attachment creates immutable cycle2; P5H2 unchanged before fixture cleanup. 519 actual original BOX3 goods/LOAD/DEPART/cost2.25, 520 forged clock and foreign warehouse denied.

Начало — первое подтверждённое сканами HU_ATTACH/HU_REPACK вложение в пустую BOX через существующее ядро. Создание пустого контейнера не создаёт начало. Добавление/удаление части содержимого сохраняет начало цикла; полное опустошение и новое вложение создают следующий цикл. Сборка вложенной пустой тары является началом упаковочной работы, количество товара от этого не возникает.

RRL_HU_PACK_CYCLE сохраняет UID, начальную версию состава, исходную operation, склад, исполнителя и timestamp with time zone. История неизменяема, защищена контекстом ядра и блокировкой HU. Событие пишется в той же транзакции, что связь и версия; rollback убирает всё. Никаких изменений остатка этим механизмом нет.

RRL_STOCK_HU_READ добавляет packing_start только при наличии настоящего нового события. Исторические коробки не получают выдуманное начало. Архив погрузки сохраняет точное событие и версию. Перенос целой коробки не объявляется новой сборкой.

[Миграция](../../db/migrations/2026-10-12_ni041_box_packing_clock/apply.sql), 2026-10-12-516-box-physical-packing-clock. Прежние native bodies сохранены. При наличии фактов rollback запрещён, требуется forward repair без удаления истории.
518 подготовлен общий readonly resolver CASE/BOX: подтверждает точное событие/версию/склад и часовой пояс; финансовые preview и guard используют один источник. Старые BOX без события явно INCOMPLETE. Применение ожидается.

Complete packing clock history is retained after test stock cleanup. ctx517/519 must not be reset; source519 is already departed/charged. Multiple-day physical scenario remains independent evidence pending.
