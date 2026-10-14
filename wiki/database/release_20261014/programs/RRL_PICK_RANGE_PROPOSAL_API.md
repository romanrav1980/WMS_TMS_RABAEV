# RRL_PICK_RANGE_PROPOSAL_API

Тип: **PACKAGE**. Схема: `RABAEV`.

Подсистема по имени: Отбор и волны.

## Интерфейс

| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |
|---|---|---|---|---|---|---|
| EXECUTE_COMMAND | P_OPERATION | 1 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_ACTOR | 2 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_ACTION | 3 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_WARE | 4 | NUMBER | IN | N |  |
| EXECUTE_COMMAND | P_ARTICLE | 5 | VARCHAR2 | IN | N |  |
| EXECUTE_COMMAND | P_REQUEST | 6 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_SOURCE | 7 | CLOB | IN | N |  |
| EXECUTE_COMMAND | P_RESULT | 8 | CLOB | OUT | N |  |
| WRITE_ALLOWED |  |  | NUMBER | OUT | N |  |

## Потенциальные записи по тексту SQL

[RRL_PICK_RANGE_CANCEL](../tables/RRL_PICK_RANGE_CANCEL.md), [RRL_PICK_RANGE_OPERATION](../tables/RRL_PICK_RANGE_OPERATION.md), [RRL_PICK_RANGE_PROPOSAL](../tables/RRL_PICK_RANGE_PROPOSAL.md)

Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.

## Зависимости

[RRL_ARTICULS](../tables/RRL_ARTICULS.md), [RRL_HAS_WRIGHT](../programs/RRL_HAS_WRIGHT.md), [RRL_PICK_RANGE_APPLY_CORE](../programs/RRL_PICK_RANGE_APPLY_CORE.md), [RRL_PICK_RANGE_APPROVAL](../tables/RRL_PICK_RANGE_APPROVAL.md), [RRL_PICK_RANGE_CANCEL](../tables/RRL_PICK_RANGE_CANCEL.md), [RRL_PICK_RANGE_OPERATION](../tables/RRL_PICK_RANGE_OPERATION.md), [RRL_PICK_RANGE_PROPOSAL](../tables/RRL_PICK_RANGE_PROPOSAL.md), [RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_STOCK_LOCK_API](../programs/RRL_STOCK_LOCK_API.md), [RUSERS](../tables/RUSERS.md)

## Кто использует

[RRL_PICK_RANGE_PROPOSAL_API](../programs/RRL_PICK_RANGE_PROPOSAL_API.md), [RRL_PR_CANCEL_G](../programs/RRL_PR_CANCEL_G.md), [RRL_PR_OPERATION_G](../programs/RRL_PR_OPERATION_G.md), [RRL_PR_PROPOSAL_G](../programs/RRL_PR_PROPOSAL_G.md), [RRL_RA_ALLOW_REPL_G](../programs/RRL_RA_ALLOW_REPL_G.md), [RRL_RA_APPROVAL_G](../programs/RRL_RA_APPROVAL_G.md), [RRL_RA_DRAIN_CLOSE_G](../programs/RRL_RA_DRAIN_CLOSE_G.md), [RRL_RA_MEMBER_G](../programs/RRL_RA_MEMBER_G.md), [RRL_RA_STATUS_G](../programs/RRL_RA_STATUS_G.md)

## Исходный код

[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `RRL_PICK_RANGE_PROPOSAL_API` в файле соответствующего типа.
