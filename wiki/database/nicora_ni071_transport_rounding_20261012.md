# NI07.1: единое финансовое округление статьи

Migration2026-10-12-594-transport-article-rounding приводит новое native проведение к существующему finance.domain.amount.cost_amount: сначала точное quantity × rate, затем HALF_UP до2 знаков по статье. Первоначальная582 округляла единичную ставку до умножения; при2 ×4.125 получалось8.26 вместо8.25. Этот избыточный вариант устраняется.

Сохранённые586 строки имеют quantity1 и107.25: перед новой CHECK используется Oracle VALIDATE, история и сохранённые ответы не переписываются. Claim/replay/outbox/права/TT→norm lock order остаются прежними. Свежий native исходник и имя старой CHECK захвачены до применения, rollback сначала проверяет совместимость всех фактов с прежним правилом и отказывает при несовместимых суммах. Подчёркивается денежный контракт существующих NUMBER(27,2), не заявление о налоговых правилах любой валюты.

[SQL](../../db/migrations/2026-10-12_ni071_transport_rounding/001_api.sql), живое применение/VALID и exact retained replay ещё предстоят. Отдельного большого стенда/копии базы не создаётся.

594 applied4 statements/0 errors, USER_ERRORS[]/INVALID[], new CHECK validated against existing financial rows. Retained586 exact read remains107.25; no financial history rewritten. Current native AMOUNT = round(QUANTITY*RATE_VALUE,2).
