from pathlib import Path
import json
out={}
p=Path('db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json');m=json.loads(p.read_text(encoding='utf-8'))
for directory in ['2026-10-12_ni061_group_source','2026-10-12_ni061_group_receive']:
 value='../'+directory+'/apply.sql'
 if value not in m['additional_scripts']:m['additional_scripts'].append(value)
out[p.as_posix()]=json.dumps(m,indent=2)+'\n'
page='wiki/database/retailcase_ni061_group_receipt_20261012.md'
out[page]='''# Единый план и атомарная приёмка многотоварного грузового места
403 и409 APPLIED, compiled objects VALID. Inventory owns group header and perlot facts; original RRL_STOCK_INTERWARE_REC delegates validation/lock planning to RRL_IW_GROUP_REC and remains the quantity executor through the existing balance/unit cores. No second quantity writer.

Actual404–406: two fresh SAP-backed full-pallet picks in one warehouse, each3EA; two original ST, two distinct articles, card matrices2+1, sixoriginalunits/ninecodes. Existing assignment/wholeHU QC/load/depart reused. Source shipping zone IS_SYSTEM=1 explicitly permits multiple physical leaves.

407 immutable grouped source plan: exact departed HU archive, members/whole distinct leaf association, container/link epochs, original issued-unit fingerprints, perarticle profiles, source zero stock, source has no recipient receipt and no scalar plan. Source signature binds dispatcher intent. Current dispatcher authorization precedes cached replay; metadata CONFIG X and ordered TT locks serialize plan creation. Group and scalar source plans are mutually exclusive.

412 actual target unload then one root receipt: both3EA stock leaves restored together, six oldunits moved ISSUED→AVAILABLE preserving birth/code provenance, same TOP restored with two appended links and closed originallinks retained. Target receiving cells are unavailable for picking. Peritem barcode/quantity/UOM and full perSKU unit/profile/version matrix required; no partial or aggregate-only group bypass. Whole late rollback undoes bothstocks/unitchanges/header-lines/links/events/outbox. Actualrepeat returns originalresult. Original customer fulfillment is not repeated; unrelated P20/H20 remains.

The single existing unit owner now accepts exact selected lot proof from domain.lots[*] in addition to old scalar source proof, retaining all lock/version/issued/quantity checks. Event line numbers are distinct perlot. JSON_EQUAL compares revalidated domain structurally after stripping reserved new-link IDs; JSON object property order is not business state.

403/409 files under db/migrations mirror live changes. SourceJSON remains immutable. RRL_EVENTS legacy ID_EVENT lacks an eligible unique key for an FK: line guard requires exactly one matching native operation/lot/qty/UOM/target event, rather than changing the historic journal schema.

SQL415: native grouped source34.548ms/5 calls; first groupplan INSERT419.928ms cold/2032buffers including trigger source validation; group lineINSERT13.159ms/5, scan registry3.309ms/20. Decision inventory: preserve existing group load uniqueness/target index and bounded200nodes/10000units; batch archive-member/profile checks before high-leaf load, ownerinventory backlog. No industrial throughput claim.

Next: existing whole-HU placement task and group custody/onward linkage; operator UI; aggregate-only/partialgroup receipt; independent/hardware/currentERP/GovACK. Retained context406 has actual receipt412 and available blocked stock. Never rerun source404/405 factories or case407 initial source eligibility after receiving.
'''
for filename,entry in [('wiki/index.md','- [Приёмка многотоварного места](database/retailcase_ni061_group_receipt_20261012.md):403–412 exacttwoST/twoSKU3each/6oldunits9codes/one rootreceipt/restoredTOP/rollback-replay; placement next.\n'),('wiki/log.md','\n- 12.10.2026 403–416: newgroup sourceplan exactdeparted archive/twooriginalST/twoSKU/matrices2+1/6units9codes; source-shared metadata source plan exclusion. Root409 unload/receipt owner remains existing INTERWARE_REC/balance/unit cores; bothstock3 restored/oldkeys/oneTOP two newlinks/quarantine/rollback/replay/P20H20. Singleunitproof extended by exact domain.lots proof; distincteventline numbers; structuralJSON revalidation. SQLsource34.548ms/coldplan419.928ms/line13.159ms: bounded/index retained, batchinventory backlog. Group placement/custody/onward/UI still open.\n'),('wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md','\n403–412 group first-leg receiving actualtwoSKU3each/sixoldunits/ninecodes/oneTOP/twooriginalST; native atomicstock+units+links+events/outbox/whole rollback/replay/noFFrepeat. Group placement/custody/onward/UI remain; see group_receipt page.\n')]:
 p=Path(filename);old=p.read_text(encoding='utf-8');out[filename]=entry+old if filename=='wiki/index.md'else old+entry
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');m=json.loads(p.read_text(encoding='utf-8'))
for x in m['increments']:
 if x['id']=='NI06.1':
  x.setdefault('implementedSlices',[]).append('403–412 whole group firstleg2ST/2SKU3each/6oldunits9codes/atomic rootreceipt+restoredHU/rollback/replay')
  x['remainingScope']=['group receipt whole-HU placement/custody/onward and operator UI','partial/aggregate-only grouped receiving','aggregation invalidation/repacking lifecycle','independent acceptance/hardware/current real ERP and government ACK']
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+'\n'
p=Path('wiki/runbooks/retailcase_active_work.md');t=p.read_text(encoding='utf-8').replace('Current native388/app373','Current native409/app411')
t=t.replace('Next: groupedmultiSKU firstleg receiving;','Latest403–412: actual grouped twoSKU firstleg receipt/6originalunits9codes/oneTOP restored, ctx406 receiving blockedstock3each; factories404405 must not rerun. Whole-HU placement/custody/onward next.\n\nNext: group whole-HU placement/custody/onward/UI;')
out[p.as_posix()]=t
root=next(Path('.').glob('*/NI08.1/178_container_cell_index.md')).parent.parent
out[(root/'NI06.1/416_group_receipt.md').as_posix()]='# Qwen403–412\nRetainedctx406 contains source404405(twoSKU/differentprofiles), original2ST/groupHU shipment, immutablegroupplan407 and actualrootreceipt412. Verify source3each/target3each blocked/same6keys9codes/oneTOP twoactive newlinks/oldclosedlinks/nativeevents distinctline numbers/rootoutbox/idempotency/current actor and profileversions/noFFrepeat/protected20. Do notrerun factories/sourceproof after actualreceiving. Independent/industrial/hardware/GovACK notclaimed. Group placement and onward remain.\n'
print(json.dumps(out))
