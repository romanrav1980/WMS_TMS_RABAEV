# Store profile → native transport: minimal contract before DDL

14.10.2026. Read/design only. No runtime changes or DDL. Basis: Claude C0025/store_profile_design.md; current native RRL_TRANSPORT_PLAN_RULES, RRL_VEHICLE_PROFILE_API, RRL_TT_TIME_API and RRL_TT_ROUTE_SCHEDULE.

## Required fields / semantics for Claude

- STORE_ADDR uses actual ADDR VARCHAR2(255); PROFILE_VERSION monotonic; immutable history and expected_version/replay as proposed. No second address identity.
- MAX_VEHICLE_HEIGHT_MM and MAX_VEHICLE_LENGTH_MM: positive integer millimetres, NULL means no configured constraint, zero invalid. These are **external overall vehicle dimensions**, not cargo-space dimensions. Name/label must say so.
- Add explicit RECEIVING_WINDOW_MODE = UNCONFIGURED or WEEKLY. UNCONFIGURED has no weekly rows and does not silently mean open24h. WEEKLY means listed intervals are the complete weekly availability; missing day is CLOSED. This avoids an ambiguous empty array. Profile absent behaves UNCONFIGURED.
- One TIMEZONE_REGION for weekly schedule, mandatory in WEEKLY, validated against actual Oracle timezone catalog; do not default from browser, warehouse or guessed country. Do not repeat differing timezones per interval. If table keeps timezone on each row, enforce same explicit zone within profile and preserve it even when all days are closed.
- WEEKDAY ISO1=Monday..7=Sunday; 0<=FROM_MINUTE<TO_MINUTE<=1440; half-open intervals, no overlap, stable ordering/identity. Overnight interval represented explicitly as two days. Store multiple intervals without merging lunch-break gaps. Concrete bounded count: at most8 intervals/day,56/week; reject beyond bound in API/native setter, never truncate.
- Editing window rows must advance PROFILE_VERSION in the same CONFIG transaction; no direct child-row edit bypass. Current profile version and all rows must be mutually consistent.

## Vehicle source: confirmed missing external dimensions

Live USER_TAB_COLUMNS: RRL_TR_VEHICLE has ID, NUM, TR_TYPE, MARKA, REF_REJIM, WORKING_NOW, PALLETS, BLOCKED, GIDROBORT, SOBSTVENNYY, DOVERENNOST_OT, MAX_WEIGHT_KG, DELETED. No physical outer height/length.

RRL_VEHICLE_PROFILE_HIST currently owns CARGO_LENGTH_MM/CARGO_WIDTH_MM/CARGO_HEIGHT_MM, VERSION_NO, RESULT_JSON. Those are cargo compartment dimensions; do not substitute them for overall road-clearance dimensions, infer from vehicle class or add body thickness guesses.

Required separate fleet-owner additive contract: OUTER_HEIGHT_MM and OUTER_LENGTH_MM (positive mm, unknown allowed), versioned through existing RRL_VEHICLE_PROFILE_API.configure/history and describe_profile. A store limit with unknown or stale vehicle outer profile must prevent final admission; draft returns explicit missing-dimension warning. Known exceeding dimension is incompatibility. With no corresponding store limit, unknown external dimension does not impose a new blanket rejection. Equality is allowed. No vehicle DDL authorised by this design alone.

## Weekly defaults versus materialized ST windows

Authoritative current fields: RRL_SBORKA_PALLETS.ZONE_TIME_PLAN_IN/OUT are concrete dated windows. RRL_TT_TIME_API.snapshot already includes both per member; RRL_TT_ROUTE_SCHEDULE.calculate currently intersects windows across members of one stop (max opening/min closing) and preserves TW_STRICT soft warning versus hard rejection.

Proposed minimal precedence: a complete valid concrete ST interval wins; weekly intervals are defaults only where both concrete fields are absent. One missing endpoint or reversed interval is invalid, not silently repaired by defaults. Record window_source=ST_MATERIALIZED or STORE_WEEKLY plus profile version/timezone; do not overwrite ST fields merely to preview. Missing both with UNCONFIGURED remains existing missing-window refusal. A weekly closed day yields no allowed interval, not midnight-to-midnight availability.

For weekly defaults, resolve actual calendar intervals in explicit store timezone over the bounded route date range, convert to the approval timezone explicitly; never infer warehouse timezone. If planning timezone is unavailable, return configuration-required. The native calculator selects a feasible interval that contains complete unload duration; waiting crosses to the next allowed interval and preserves breaks. For multiple ST at a stop, intersect each member's allowed interval set; do not collapse several windows to min/max envelope. Concrete ST intervals retain their precedence; if weekly calendar must instead be a mandatory additional constraint even for existing ST, that is a different business rule requiring explicit decision, not an implicit change here.

Keep RRL_ADDR.TW_STRICT as sole strictness field; soft miss remains warning, hard miss blocks approval. Weekly closed availability must be represented explicitly, so native implementation must decide/record hard closure versus soft lateness without treating a missing interval as an ordinary late bound.

## Native owners, signature and lock integration

1. RRL_TRANSPORT_PLAN_RULES existing vehicle admission (currently type/hydrolift/tonnage/floor) calls a small native store-access helper for dimensions, used by manual/solver/final physical admission through existing owners. No Python shadow validator.
2. RRL_TT_TIME_API.snapshot adds ordered destination profile identity(version or explicit absent), relevant limits, window mode/timezone/canonical rows; resolved vehicle ID + current fleet profile version/base hash and external dimensions. Bump source contract version when adopted. Profile edits invalidate prior source_hash even when current ST window wins, conservatively and visibly.
3. RRL_TT_ROUTE_SCHEDULE is the single weekly resolver/calculator for preview and final approval. Existing sequence CONFIG via RRL_STOCK_METADATA_TX → TT → sorted ADDR/matrix locks → fresh snapshot/hash remains authoritative. Both profile setter and fleet setter participate in existing CONFIG fence, including create/absent profile; do not add an earlier-ranked lock after TT. Read profile rows only under the fence for final approval; re-read source after lock_material, compare expected source_hash/version. Native current-config check also belongs at existing final admission; a cached Python card is not proof.
4. Existing approve replay returns original immutable result. Config change makes a prior approval stale for future use; it must not rewrite its history or reinterpret replay as fresh approval.

## Avoid duplicate fields

Do not duplicate ADDR.TW_STRICT, UNLOAD_NORM_MIN, MAX_VEHICLE_TONS, TRANSPORT_TYPE, STOL, coordinates/geofence, SHIPPING_TIME. SHIPPING_TIME is warehouse shipping time, not receiving-window default. SAP warehouse delivery weekday/calendar exceptions remain separate; this profile does not override SAP order availability. Customer-address capacity is not automatically backroom capacity; no proven direct identity permits replacing it. Ramp height is not overall vehicle height or GIDROBORT. Contact e-mail already exists in ADDR.EMAIL; phone/role may be new. Unattended drop must not bypass existing store receipt/marking proof merely because metadata flag is true.

## Handoff

Claude can complete versioned profile storage/API/UI with window mode+explicit timezone and correctly labelled store limits. Root owns subsequent fleet outer-dimension extension and native admission/window integration after contract agreement. Do not report configured restrictions as enforced until native integration is applied and one bounded real scenario confirms it. No new tests/DDL performed in this design task; one metadata-column query only.
