# Independent bounded review: store access dimensions

Reviewer: Codex store_schedule (not author). 2026-10-14. One read-only source pass; no new tests, DDL, runtime mutations, or general audit.

**Result: no material correctness findings in the reviewed change.** This is a scoped source review, not proof of all physical workflows or a replacement for the author's native evidence.

Scope: migration `2026-10-14_ni022_store_access_dimensions/001_access_helper.sql`; changed hunks plus surrounding control flow in `002_plan_rules.sql`, `003_load.sql`, `004_depart.sql`; supporting README and existing native report. Compared the three caller bodies with saved pre-change sources.

- **Draft completeness cannot bypass the added physical checks.** `check_sts` delegates validated0/1 completeness to the helper; unknown/stale required dimensions produce draft-incomplete material for0 and refusal for1. `assert_members` always passes1. Both physical callers invoke it unconditionally; they do not forward a client p_complete flag.
- **Final CONFIG protection is explicit.** `assert_members` requires CONFIG/WAREHOUSE mode4 before reading profile data. Existing owner writes use exclusive6, including first profile creation. Departure compilation includes the CONFIG fence; calling a final without the fence fails rather than silently skipping the check. Existing final vehicle/trip locking and member closure checks remain in place. No new earlier-ranked lock was added.
- **Current data and unknowns:** helper resolves actual member IDs to current destinations, rejects missing members, reads the current READY vehicle profile once, and uses only outer dimensions. Missing/stale required dimension refuses final. Known excess rejects both draft and final, equality passes. An unconfigured store limit does not impose a new universal dimension requirement.
- **Legacy address behavior:** NULL DELETED3 is treated as active. A configured limit on missing/deleted address refuses. Null destination is skipped by the additive access-limit lookup; this preserves pre-existing lookup semantics rather than inventing a profile. Physical load already refuses null ST destination in compile_load and checks frozen destinations in finish_load. This review does not claim the helper is a general destination-integrity validator for every legacy path.
- **No duplicate stock effect:** helper is read-only; inserted calls occur before existing physical effects. No additional movement, inventory writer, commit, outbox insertion or replay interpretation was introduced. Departure still uses the original operation/closure path.
- Existing empty draft remains valid as a draft; it cannot reach `assert_members` because finals require1..200 members. Counts/list validations and bounded destination collection are explicit.

No remedial patch requested. Shared code/wiki/index/log untouched. Author/root own installed-source verification and native/physical acceptance; this reviewer did not rerun them.
