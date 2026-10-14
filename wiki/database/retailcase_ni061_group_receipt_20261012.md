# Единый план и атомарная приёмка многотоварного грузового места
403 и409 APPLIED, compiled objects VALID. Inventory owns group header and perlot facts; original RRL_STOCK_INTERWARE_REC delegates validation/lock planning to RRL_IW_GROUP_REC and remains the quantity executor through the existing balance/unit cores. No second quantity writer.

Actual404–406: two fresh SAP-backed full-pallet picks in one warehouse, each3EA; two original ST, two distinct articles, card matrices2+1, sixoriginalunits/ninecodes. Existing assignment/wholeHU QC/load/depart reused. Source shipping zone IS_SYSTEM=1 explicitly permits multiple physical leaves.

407 immutable grouped source plan: exact departed HU archive, members/whole distinct leaf association, container/link epochs, original issued-unit fingerprints, perarticle profiles, source zero stock, source has no recipient receipt and no scalar plan. Source signature binds dispatcher intent. Current dispatcher authorization precedes cached replay; metadata CONFIG X and ordered TT locks serialize plan creation. Group and scalar source plans are mutually exclusive.

412 actual target unload then one root receipt: both3EA stock leaves restored together, six oldunits moved ISSUED→AVAILABLE preserving birth/code provenance, same TOP restored with two appended links and closed originallinks retained. Target receiving cells are unavailable for picking. Peritem barcode/quantity/UOM and full perSKU unit/profile/version matrix required; no partial or aggregate-only group bypass. Whole late rollback undoes bothstocks/unitchanges/header-lines/links/events/outbox. Actualrepeat returns originalresult. Original customer fulfillment is not repeated; unrelated P20/H20 remains.

The single existing unit owner now accepts exact selected lot proof from domain.lots[*] in addition to old scalar source proof, retaining all lock/version/issued/quantity checks. Event line numbers are distinct perlot. JSON_EQUAL compares revalidated domain structurally after stripping reserved new-link IDs; JSON object property order is not business state.

403/409 files under db/migrations mirror live changes. SourceJSON remains immutable. RRL_EVENTS legacy ID_EVENT lacks an eligible unique key for an FK: line guard requires exactly one matching native operation/lot/qty/UOM/target event, rather than changing the historic journal schema.

SQL415: native grouped source34.548ms/5 calls; first groupplan INSERT419.928ms cold/2032buffers including trigger source validation; group lineINSERT13.159ms/5, scan registry3.309ms/20. Decision inventory: preserve existing group load uniqueness/target index and bounded200nodes/10000units; batch archive-member/profile checks before high-leaf load, ownerinventory backlog. No industrial throughput claim.

Next: existing whole-HU placement task and group custody/onward linkage; operator UI; aggregate-only/partialgroup receipt; independent/hardware/currentERP/GovACK. Retained context406 has actual receipt412 and available blocked stock. Never rerun source404/405 factories or case407 initial source eligibility after receiving.
