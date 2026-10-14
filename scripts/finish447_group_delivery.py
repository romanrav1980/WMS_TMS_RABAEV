from pathlib import Path
import json
out={}
p=Path('db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json');m=json.loads(p.read_text(encoding='utf-8'))
for directory in ['2026-10-12_ni061_group_promises','2026-10-12_ni061_group_custody','2026-10-12_ni061_group_onward','2026-10-12_ni061_group_thermal']:
 value='../'+directory+'/apply.sql'
 if value not in m['additional_scripts']:m['additional_scripts'].append(value)
out[p.as_posix()]=json.dumps(m,indent=2)+'\n'
page='wiki/database/nicora_ni061_group_delivery_20261012.md'
out[page]='''# Полный многотоварный межскладской поток двух плеч
428/429/433/442 APPLIED/VALID. Existing custody/shipping/HU/task/store owners retained; group helpers describe sources and immutable links, not another quantity writer.

Actual context406: first HU_GROUP406 withtwooriginalST/twoSKU3EA/sixbornkeys/ninecodes →immutablegroupplan407 →wholeunload/receipt412 into blockedreceiving →existingHUtask419 quantity1HU/twocommodity3EA →custody430 →existingST constructor/groupOnward435/oldassignment/QC →samewholeTOP secondload436 →departure437 →existingSTOREreceipt accepted3 for eachoriginalorder2070/2071. SourceFF3 once each, targetP0, sixbirthunits/ninecodes unchanged; unrelated20/20 preserved. Secondload late rollback undid both stock/dispatch effects; native/HTTP replay stable.

New RRL_IW_GROUP_ST_BIND associates eachoriginal source ST and exactfree placed lot/currentstockversion/frozenrecipient/oldfulfillment. RRL_STOCK_INTERWARE_NEXT delegates group describe/declare/validate/dispatch alongside original/recovery branches. Existing shippingcore consumes stock; composite groupdispatch OP+ST/perSToutbox preserves two source lineages. Whole-HU group loading is supported; detached individual LOAD_SHIPMENT is deliberately refused pending separate integration.

Original departure promises now include groupplans and require all exact perlot APPLIED/native target loads. Before secondload430 group promisefalse; after436 true. Incoming read includes group perSKU rows and recognizes actualLOADED/DEPARTED evidence; actual440 shows2/2 ready. This readiness is not legal/driver/vehicle departure authorization.

Delivery source projection438 follows distinctgroup firstload→secondload mapping. DISTINCT matters: two dispatch facts sharing onefinal load must not multiply its receipt lines. Actual originalorders eachshipped3/accepted3/unreceived0. Perlot quantity ownership retained. Existing RRL_STORE_RECEIPT_LINE is authoritative customer receipt quantity evidence.

442 group receive/placement/onward checks current targetWARE SKU temperature ranges through existing RRL_INTERWARE_THERMAL.assert_cell. No parallel thermal calculation. Group HOLD/override/observation and routing revisions remain separate backlog; defaults match existing perWARE rules. Native helper throws for invalid/incompatible configuredranges. Dispatch receipt index added for bounded group phase lookup.

Raw interwarehouse-groups page and typedAPI include full plan/unload/receive/placement/custody/onward. Saved operation/scanner draft survives uncertainresponse; current actor/API scope reset; schema422 permits correction without retrying a nonexistent command. API restarted via absolute serv.bat at445. Actual444 HTTP delivered2/incomingready/exact oldreceipt+placement replay after delivery. Source/constructor factories404405 and intermediate receiving/P3 assertions must never rerun.

SQL440 groupbind lookup.907ms/12, resolveddispatchproof3.762ms/4, dispatchINSERT8.999ms/4; phase aggregate20.403ms cold/59buffers. Decision inventory/delivery: existing ST uniqueness/sourceindex retained; added receipt index442. High-leaf source/profile/archive batching remains ownerinventory backlog (source34.548ms/coldplan419.928ms earlier415). No million-operation/hardware/legalGovACK/independent acceptance claimed.

Remaining: partial/aggregate-only groups, multi-day/temperature decisions and revisioned rerouting, detachedsingle loading, high-leaf batching, real ERP/Gov/hardware/independent acceptance.
'''
for filename,entry in [('wiki/index.md','- [Полная доставка многотоварного места](database/nicora_ni061_group_delivery_20261012.md):428–444 twoSKU3each/originalST→groupreceipt/1HUtask/custody/onward/LOAD/DEPART/STOREbothbuyer3; sourceFFonce/6oldkeys9codes/HTTP replay.\n'),('wiki/log.md','\n- 12.10.2026 428–447: closedboundedgroup two-legactualctx406/twoSKU3EA6keys9codes/originaltwoST/firstreceipt412/wholetask419/custody430/onward435/originalshipping436/depart437/STORE3each. Group promises block beforeload/readyafter, incoming2/2; delivery438 distinctlineage avoids doublecount. SourceFF3once each/protected20; fullloadrollback/replays and restartedHTTP444 exactoldcommands afterdelivery. CurrentperSKU temp assertions reuseoldthermalowner442/receipt index; groupdecisions/rerouting/partials/aggregate-only remain. SQLbind.907/dispatch8.999/phase20.403ms bounded/indexbatchowner decisions.\n'),('wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md','\n428–444: full positive twoSKU firstleggroup receipt→originalHU task→custody→existingnewST/assignment/QC→wholeHU secondLOAD/DEPART→STORE3each. Old6keys9codes/sourceFF3once/native rollback/replay/HTTP afterdelivery/currentthermalcellrules. Group departure promises and incoming2/2, originalorder delivery projection DISTINCT correct. Partial/aggregate-only/temperaturedecision-rerouting/highleaf/independentexternal remain.\n')]:
 p=Path(filename);old=p.read_text(encoding='utf-8');out[filename]=entry+old if filename=='wiki/index.md'else old+entry
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');m=json.loads(p.read_text(encoding='utf-8'));m['date']='2026-10-12';m['planRevision']=14;m['currentSprint']='NI04.3'
for x in m['increments']:
 if x['id']=='NI06.1':
  x['status']='in_progress_grouped_two_leg_delivered'
  x.setdefault('implementedSlices',[]).append('428–444 full grouped2SKU3each/old6keys9codes/custody/ST/wholeload/depart/STOREbuyer3each/sourceFFonce/groupdepartureincoming/typedUI/HTTP replay')
  x['remainingScope']=['partial/aggregate-only grouped receiving','group temperature decisions and revisioned rerouting/detached single loading','aggregation invalidation/repacking lifecycle','high-leaf source batching and independent acceptance/hardware/current real ERP and government ACK']
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+'\n'
p=Path('wiki/runbooks/nicora_active_work.md');t=p.read_text(encoding='utf-8').replace('Current native417/app425','Current native442/app441, APIserv445')
t=t.replace('APIserv366 (latest invoice-period read373 pending restart)','latest group/billing period reads loaded')
t='Latest447: ctx406 fullgroup two-leg delivered/STORE3each/sourceFF3once each/old6keys9codes/P0; nofactory404405 or receiving419 interimassertions. Native442/currentAPI445/HTTP444 replaypassed. Next NI04.3 aggregate invalidation/repacking lifecycle; grouppartials/thermalrerouting remain.\n\n'+t
out[p.as_posix()]=t
root=next(Path('.').glob('*/NI08.1/178_container_cell_index.md')).parent.parent
out[(root/'NI06.1/447_group_delivery.md').as_posix()]='# Qwen428–444\nRetainedctx406: actualfullfirstgroup2SKU3each/6oldkeys9codes→receipt412→task4191HU+2commodity3→custody430→existingST435→wholeload436 rollback/replay→depart437→STOREbothorders3/sourceFF3once each/P0/protected20. Verify distinctsource/final-load projection avoids duplicatecount; groupNative departurepromise falsebefore/trueafterload/incoming2/2. HTTP444 exactreceipt+placementreplay afterdelivery; API445 current. Warehouse group state and typedUI intents independently verify. No initialfactories or intermediateP3 receivingassertions. Grouppartial/aggregate-only/thermaldecisions/rerouting/hardware/GovACK/independent acceptance notpassed.\n'
print(json.dumps(out))
