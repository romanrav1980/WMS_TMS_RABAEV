# Qwen:230 — маркированная единица и расхождение
Свежая изолированная full standalone source->native picking/QC/load/depart->interware plan/receipt/placement/custody/onward/depart. Не повторять уже принятыйd76ea1c478/order2031.
Три физических единицы/по2профиля: scan all mandatory codes of units1/2 ACCEPTED, unit3 absent ->exact accepted2/missing1; legacy observations accepted2 missing1 reason mandatory. Количество кодов4 не количество товара4.
Positive variants on fresh source: unit1 ACCEPTED, unit2 REFUSED, unit3 DAMAGED, all applicable profiles per present unit. Each unit/profile action must match, exact base quantities/scale/UOM/source versions. Source control whole original issued fingerprint.
Incomplete profile/duplicate/foreign code/mixed actions/quantity mismatch/unproven extra ->refusal/no fact. Zero scans only valid when declared exact entire source missing with reason, never default full acceptance.
Native outerrollback removes receipt/unit facts/case/obligations/outbox together; concurrent two IDs one winner; replay stable; current bound receiver scope retained.
RRL_STORE_RECEIPT_UNIT row links actual old physical key/source version/load/receipt, append-only; raw inserts/edits/deletes refused/rootless. Existing physical-key unique index reused FK constraint, no duplicate index.
Order2031 actual semantics PARTIALLY_ACCEPTED shipped3 accepted2 missing1 unreceived0: все решения известны, одна недостача; не писать unreceived1. Case remains open until independent owner resolution.
Warehouse sum0H0/units3 ISSUED unchanged/codes6/no new unit births or stock events/GovACK. Positive warehouse return not implied.
React scanner per-unit decision/profile/Enter/durable draft; old full default ACCEPTED normalizes without new hash fields, verify SAME229 saved full receipt replay unchanged. Source/profile/auth switch and partial quantity reason match native.
New plan from actual freshly committed source must not bind decoded Oracle dict as CLOB: native helper on table COMPOSITION_JSON in same cursor/TX. Diagnose stale worker before generating duplicate source.
Review slowSQL code hash/source indexed join<=20k/current units<=10k, unique source facts/explicit decision.
