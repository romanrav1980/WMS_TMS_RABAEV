# Geofence contract repair — RELEASE

14.10.2026. Existing RABAEV/orcl, no DDL.

Live USER_TAB_COLUMNS confirms ADDR VARCHAR2 is the address key; no ID/LATITUDE/LONGITUDE. SHIROTA/DOLGOTA NUMBER, DELETED3 and GEO_FENCE_RADIUS_M exist. Existing store directory already aliases the same fields. RRL_TR_VEHICLE uses NUM. RRL_SBORKA_PALLETS has CONDITION, no DELETED/DELETED3; existing dispatch predicate CONDITION<>2 reused.

GET now uses actual coordinates, excludes deleted addresses and null/out-of-range coordinates, retains legitimate zero coordinates, bounds200, preserves masked search. addr_id is the actual string ADDR; additive addr_key is explicit. No invented numeric0 or generated identity. No existing frontend geofence caller was found.

PATCH accepts the real address (path converter supports slash), validates positive integral radius and returns404 for absent/deleted address. Native RRL_STOCK_METADATA_TX with warehouse_settings_edit and CONFIG then row lock protects the change; endpoint now requires that edit permission, not view-only access. No new business writer or permissions were added.

GPS lookup corrected the same native fields and vehicle NUM. Coordinates validated before ingestion. State distinguishes (trip,address). GPS ENTER/EXIT now reports operational_fact_applied=false, reason=unambiguous_binding_required. Removed old auto update of arbitrary first UNLOAD by ROWNUM1: operation table has no ADDR/ADDR_ID and no authoritative matching operation was found. Observations are not unloading completion. No real vehicle GPS was submitted.

## Evidence

[native.json](native.json): actual FastAPI router through TestClient with real auth/Oracle. GET200/200rows; own NI081.SHOP.0b960a9257 radius200→213→read→restore200 through existing CONFIG. Invalid0→422; slash missingaddress→404. Real GPS lookup for impossible vehicle returns[] without mutation. Initial scoped run exposed additional invalid legacy SP.DELETED; corrected using existing CONDITION predicate, final run PASS.

scripts/geofence_observation_case.py: two trips sharing one address produce independent enter/exit observations, repeated same position does not duplicate enter; any attempted operational write fails the test. PASS.

Oracle SQL: unfiltered list16.602ms average/15buffers per execution; masked3.296ms/16buffers; native empty GPS lookup first parse138.68ms/383buffers. Decision: keep bounded200/address key and current indexes; no new index or broad performance run justified. Initial HTTP includes authentication/connection startup1619ms. API8088 restart/live deployed smoke coordinated by root.

Changed runtime: modules/transport/infrastructure/geofences.py; transport/public.py export; routers/gps.py; services/geofencing.py. Main/shared master_data unchanged. General gate/index/log handled by root.

## GPS ingestion: atomic history and current position

Follow-up repair: new transport/infrastructure/gps_ingestion.py owns one transaction. Active vehicle row FOR UPDATE WAIT5 serializes same-vehicle packets before history and LAST lookup/upsert, including first position. History preserves every valid packet; LAST updates only when observed timestamp is >= current timestamp. Missing vehicle returns404. Router is shorter and delegates the write. Stale observation does not feed geofence state.

Timestamp contract is explicit legacy Oracle DATE: YYYY-MM-DDTHH:mm:ss, database-local wall time, whole seconds, no offset. Missing timestamp uses one SYSDATE obtained inside the transaction after lock; both history and LAST receive the same time. Offset/fraction/numeric/invalid dates are422. This preserves existing DATE semantics without inventing UTC conversion. GPS access/IP-whitelist contract unchanged; production verification remains separate.

[Rollback evidence](gps_atomic.json): own transient vehicle10102, three real native packets(new/stale/equal), history3/current remains latest/equal update; full outer rollback leaves no vehicle/history/LAST. Timestamp validations PASS. No real vehicle input or shipment. This is a targeted single-session atomic/order case, not a concurrent multi-worker load claim; same-vehicle exclusion is enforced by the existing parent row lock.

SQL: vehicle row lock0.983ms average, current update3.584ms. Initial three history inserts averaged338.394ms (SQL am9g7rdb9jbu8, total elapsed1015ms vs CPU94.7ms); existing sequence is NOCACHE. Decision: no lookup index added for INSERT; bounded follow-up belongs to transport operations owner to inspect sequence/redo wait and assess CACHE sequence setting before high-rate GPS pilot. No DDL or broad load testing added to this repair. The cold targeted measurement does not establish sustained throughput.
