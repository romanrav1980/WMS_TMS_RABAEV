# C0196: operator UI for a multi-order root HU shipment (strategy)

Strategy only: no source, tests, SQL, API calls or screenshots. The basis is the accepted C0195 design and the existing UI and contracts in the repository as of 28.10. Each field below is marked **[exists]** (an existing response) or **[C0195]** (only after the server exposes the agreed contract). The UI must not show a [C0195] field before that contract is published.

## 1. Principle: no new screen
The operator already passes three existing places. The multi-order case adds one block and one action to them, not a new workspace.

| Step | Existing place (keep) | Read contract |
|---|---|---|
| A. Bind the root to the ST | raw page `warehouse-hus.html` ("HU control": `warehouse-hus.js` and `warehouse-hu-tree.js`, command journal `hu-command-intent.js`) | `GET /api/warehouse-hus/composition` [exists]; `POST /api/warehouse-hus/bind-shipment` (C0193, accepted) [exists, no UI yet] |
| B. Outgoing quality of the ST | panel "Контроль перед отгрузкой" in `warehouse-tasks.html` (`outgoing-quality.js`, intent `outgoing-quality-intent.js`) | `GET /api/outgoing-quality/{ST}` [exists, ST-level] |
| C. Pallet type of the root | `pallet-floor-type.js` inside `transport-loading.html`; for a CONTAINER root, the HU `TARE_BOOK` (C0194, Codex) | `POST /api/inventory/tare/book` [exists] |
| D. Load the whole root | `transport-loading.html`, "HU" mode (`transport-loading.js`, intent `transport-loading-intent.js`) → `HU_SHIP` | `POST /api/transport/loading/confirm` [exists] |

**Supervisor view (read-only):** the React desks `HuTreeDesk` (`HuTreeWorkspace`, `huTreeModel.parseHuSnapshot`) and the consolidation `PlanView` already show the root tree and the plan members (`fulfillment_id`, `shipment_id`, state). They need no new actions.

## 2. Shared block: "Корень → одна СТ, один получатель"
This is one read-only block, built from the existing tree parser (`parseHuSnapshot`). Steps A, B and D show it under the scanned identifier.

**Header**
- **Root:** uid / SSCC, type (PALLET/BOX), version, cell, warehouse [exists: snapshot root node].
- **ST:** number and identifier, recipient address [C0195: QC status `shipment_identifier` exists; the address should come with `slices`. Until then show "получатель: см. СТ"].
- **Summary chip** (wording follows `PlanView`: "complete" does not mean "may ship"):
  - "Один корень · одна СТ · N заказов одного получателя" when all slices agree;
  - otherwise the stop reason (see §4).

**List of CASE children:** one row per snapshot node with `kind="CASE"`, ordered by SSCC.

| Column | Source |
|---|---|
| CASE (SSCC, task no.) | node `sscc`, `case_task_id` [exists] |
| Status | node `status` (WAIT_CONTROL, CONTROLLED, …) [exists] |
| Version | node `version` [exists] |
| Composition | that CASE's STOCK children: `article`, `quantity`, `base_uom` [exists]. Show quantity in base units; never sum KG and EA. |
| Order / fulfillment | `slices[].customer_order_id`, `fulfillment_id` [C0195]. Until the contract exists show "—" with the hint "заказ будет показан после публикации серверного контракта". Do not derive the order on the client. |
| Fulfillment state | `slices[]`: PICKED plus version match [C0195] |

**Total row:** per article and base UOM, the sum of all CASEs' quantities [exists, from the snapshot `quantities`] next to the ST rows [C0195]. Highlight any mismatch. The comparison verdict comes only from the server code. The client only displays it.

**QC column: honest wording.**
- Outgoing quality is an **ST-level** fact (`ready`, `composition_signature`, `control_mode`). There is no per-CASE QC.
- So the block shows **one** QC badge for the whole ST, taken from the existing panel's states: "Контроль не требуется" / "Допуск подтверждён" / "Ожидает контроля".
- Each CASE row shows only the CASE status. The row must not display a per-CASE "QC passed".

## 3. Behaviour per step

### A. Binding (warehouse-hus.html)
**Action:** "Привязать корень к СТ", available only when the scanned identifier is a top-level PALLET/BOX with ≥1 CASE.

**Fields:**
- **ST identifier:** scan or input.
- **Expected root version:** taken from the read snapshot, never typed.
- **`operation_id`:** generated once and saved in the existing HU command journal *before* POST.
  - **Unknown outcome** (503, connection loss, `outcome_confirmed=false`): offer only "Повторить тот же запрос" (same id and body) or "Прочитать результат". A new operation is not offered.
  - **409 with `outcome_confirmed=true`:** a confirmed refusal. Clear the journal and show the reason.
  - **`operation_id_conflict=true`:** "Этот номер операции уже использован с другим содержимым". Keep the journal and offer to read.

**Success:** show the returned `cases[]` (case, fulfillment, composition, `idempotent`), then re-read the composition.

### B. Outgoing quality (warehouse-tasks.html)
- **No change to scanning or weighing.**
- **After reading the status:** if the response contains `slices` [C0195], insert the shared block above stage 1. Then set the summary line to "СТ … · N заказов · допуск по всей СТ".
- **Root identifier entered:** keep the existing behaviour (`adoptIdentifier` requires the response to name the ST). The block appears only when the server resolves the ST.
- **Weight:** the existing hint about the gross weight basis stays. The expected weight includes the root tare, which is a server fact (C0195 §5.3). The UI does not calculate it.

### C. Pallet type
For a CONTAINER root, the pallet-type form directs the operator to the HU tare booking with the root and cell scans (C0194). Nothing multi-order-specific is needed.

### D. Loading the root (transport-loading.html, HU mode)
**Before "Подтвердить погрузку", show the shared block plus three pre-check lines:**
- QC badge of the ST;
- root pallet type (booked / not booked);
- "все CASE этой СТ в корне".

These are read-only hints. The server decides.

**One action loads the whole root.** Help: "Все заказы этого корня отгружаются одной операцией; частичная отгрузка одного заказа невозможна".

**Single-ST modes:** for a multi-order ST, "SINGLE" mode and the TSD single binding (`case-pick-tsd.html`) only show the server refusal with the hint "отгружайте корень целиком в режиме HU".

**Result:** the existing `transport-loading-intent.js` journal and retry rules stay. After success, show `slices[]` [C0195]: order, fulfillment, case, allocations.

## 4. Stop reasons (operator text)
Map the codes in the existing `explain()` / `loadingError()` dictionaries; the unknown-code fallback shows the raw code. Codes marked † are C0195 proposals. Map them only after the server publishes them under those exact names.

| Code | Operator text |
|---|---|
| `ROOT_CASE_ALREADY_BOUND_TO_ANOTHER_ST` | CASE уже относится к другой СТ. Отсоедините его или выберите ту СТ. |
| `ROOT_CASE_NOT_CLOSED` | Не все CASE закрыты. Завершите сборку CASE. |
| `ROOT_CASE_VERSION_CHANGED` / `ROOT_VERSION_CHANGED` | Состав изменился. Перечитайте корень и повторите сканирование. |
| `ROOT_CASE_ORDER_NOT_UNIQUE` | Два CASE одного заказа в корне. На корень допускается один CASE на заказ. |
| `ST_RECIPIENT_NOT_SINGLE` / `SHIPMENT_MULTI_ORDER_RECIPIENT_CONFLICT`† | В корне заказы разных получателей. Один корень = один получатель. |
| `ST_FULFILLMENT_ORDERS_DIFFER_FROM_ROOT` | Заказы СТ не совпадают с заказами CASE в корне. |
| `ROOT_COMPOSITION_CHANGED` / `ST_COMPOSITION_DIFFERS_FROM_ROOT` / `SHIPMENT_MULTI_ORDER_COMPOSITION_MISMATCH`† | Состав корня не равен строкам СТ. Сверьте строки СТ с CASE. |
| `ST_ALREADY_BOUND_TO_ANOTHER_PHYSICAL_ROOT` / `SHIPMENT_MULTI_ORDER_ROOT_SPLIT`† | CASE этой СТ находятся в разных корнях. Соберите их в один корень. |
| `SHIPMENT_MULTI_ORDER_CASE_SET_MISMATCH`† | Набор CASE СТ не совпадает со сборками заказов. |
| `SHIPMENT_MULTI_ORDER_FULFILLMENT_CHANGED`† | Сборка заказа изменена после привязки. Перечитайте корень. |
| `SHIPMENT_WHOLE_HU_REQUIRED` | СТ с несколькими заказами отгружается только целым корнем (режим HU). |
| `SHIPMENT_CURRENT_COMPOSITION_QUALITY_REQUIRED:*` | Нет допуска контроля для текущего состава СТ. Пройдите «Контроль перед отгрузкой». |
| `LOAD_FLOOR_SINGLE_HELD_HU_TARE_REQUIRED` | Не подтверждён тип паллеты корня. Забронируйте тару корня. |
| `OPERATION_CONTENT_CONFLICT` / `OPERATION_CONFLICT` | Номер операции уже использован с другим содержимым. Прочитайте результат; новую команду не создавайте. |

## 5. Help text
**Help article:** add to the existing articles, `warehouse-hu-tree` and the QC/loading help pages in `docs/help/public/`. Do not create a new article. Use `data-help-id` for in-place hints, following the existing pattern.

**Short texts:**
- **Блок «Корень → СТ»:** "Один корень везёт одну СТ одному получателю. В строках — каждый CASE со своим заказом и составом. Итог сравнивается со строками СТ."
- **Колонка «Заказ»:** "Заказ и сборка, к которым привязан этот CASE. Каждый CASE проверяется по своему заказу."
- **Значок контроля:** "Допуск контроля относится ко всей СТ, а не к отдельному CASE."
- **Привязка:** "Сканируйте корень и СТ. Номер операции сохраняется до ответа; при сбое повторяйте тот же запрос."
- **Погрузка HU:** "Подтверждение погрузит весь корень и закроет все заказы СТ одной операцией."

## 6. Not invented / open dependencies
- **Per-CASE order and fulfillment, ST address, `slices` in QC and loading results:** these need the C0195 server contract. Until then the order column is "—".
- **No per-CASE QC state exists.** The UI must not imply one.
- **The C0193 bind route has no UI today.** Step A is the only new action. It reuses the existing HU command journal and response mapping (`outcome_confirmed` / `operation_id_conflict`).
- **Codes marked † are proposals.** The final names come from the server.
