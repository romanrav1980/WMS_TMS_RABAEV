# Типы, публичные границы и компактное проведение,149

Existing concrete WarehouseTask/CASE/short/MES/reservation/LotCheck DTOs and OracleGateway|TransactionGateway now type missing public/infra signatures. Native JSON result dict explicitly returned, previous incorrect complete->None fixed. TaskActionHandler moved to owner contract and bound factory Callable specifies handler/gateway. No separate business rule.

CaseCarrierReturn DTO and QualityWeightPolicyInput moved from API to owner contracts, old imports preserve alias identity. Reservation DTOs moved from enlarged schemas.py to passive inventory/contracts.py, existing schema names retained. OperationFactUpdate similarly passive transport/contracts; only aliases in schemas. No infrastructure→API or foreign private module dependency. Master_data receipt policy now shared platform public CONFIG UOW. Frontend StoreCasesPanel uses delivery public index.

StockPosting staging hint/capture preparation extracted to same-cursor typed stock_staging_inputs; existing retry/deadline/prepare/root/stage/commit/reset logic retained. Terminal old lot-check DML tail removed because148 adapter handles all active effects or refuses; protocol and scan normalization remain.

Remaining oversized legacy transport router receives actual extraction: unchanged PATCH /api/admin/transport/operations/{op_id}/fact in transport module API/port/native adapter, application composition injects original availability cache invalidation after successful commit. Existing TransportService native path retained for other legacy callers. No duplicated posting/scheduling logic. Native error class moved to passive contracts_plan, original infrastructure alias preserved.

Quality gate PASS:499files/0cycles/79 remaining recorded legacy debt; no new/grown regressions. --tighten-baseline only decreased actual allowances, thresholds unchanged.24 architecture/tooling casesPASS, both frontend TypeScript checksPASS; pytest cache directory warning did not affect result. Seventeen targeted cutover casesPASS. No full independent business acceptance.

Actual original SAP receipt replay exact/no new journal after staging extraction. Original task829 sync twice same/native event and stock/attempt timestamps unchanged. Original ARM task33530 fact preserved: old URI/openAPI present, empty400, cancelled trip409 through new endpoint, original operation list/facts unchanged. No new stock/TT. Positive new fact and positive full API CASE remain independent cases.

No Oracle migration; current native keyed writers retained. Native rule and warehouse calendar decisions unchanged. Main factual remaining NI08.1: approved physical ranges/drain/cost routes, joint exact schedule/driver validator, canonical warehouse calendar and independent acceptance.
