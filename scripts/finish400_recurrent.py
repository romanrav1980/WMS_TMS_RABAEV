from pathlib import Path
import json
out={}
page='wiki/database/nicora_ni061_recurrent_physical_20261012.md'
out[page]='''# Два физических цикла недостачи одной маркированной единицы
390–399 проведены в RABAEV/orcl через существующее единое ядро. Исходный SAP BOX1 создал только три единицы и шесть кодов.

Первое плечо: принято 1 из 3, независимо подтверждена недостача 2, найдены те же две единицы; размещены существующими заданиями и доставлены вместе с принятой частью покупателю. Исходный заказ исполнен 3 один раз.

Затем именно эти две единицы возвращены через существующий REUSE: утверждение, связанный SAP-документ, физическая передача, водитель, точные четыре QR, заблокированная приёмка и размещение в отбор. Новое плечо создано из этого доступного остатка, без новой товарной приёмки или рождения кодов.

Во втором плече принято 1 из 2, другая единица повторно утрачена и найдена. Её PHYSICAL_UNIT_KEY совпадает с первым событием; история первого события сохранена. Найденная и принятая части размещены, объединены в одно место и доставлены покупателю: новый заказ accepted2/unreceived0, historical_shortage1/recovered1/net0, FF2 один раз. На повторной погрузке поздний rollback вернул оба остатка; повтор команды дал исходный результат.

Сохранены context390/390_recovery/392/394/396/396_recovery/398. Не запускать исходные фабрики заново и не проверять промежуточный P2 после его последующей отгрузки. Шесть исходных кодов сохранены, защищённый запас другого сценария P20/H20 неизменён. Реальные внешние подтверждения и оборудование этим случаем не подтверждаются.

SQL399: recovery-ST PK lookup 4.167ms; dispatch insert 10.312ms; CASE-source lookup 13.497–16.316ms при двух исполнениях. Решение inventory/delivery: сохраняем ограниченные команды и текущие PK/FK; объединение повторных CASE-source lookup в пакетную проверку — backlog владельца delivery при многолистовой нагрузке. Миллионную нагрузку не заявляем.
'''
for filename,entry in [('wiki/index.md','- [Два физических цикла недостачи](database/nicora_ni061_recurrent_physical_20261012.md):390–399 samekey/loss-found→buyer→REUSE→newshipment→loss-found→buyer2; original6codes/no rebirth.\n'),('wiki/log.md','\n- 12.10.2026 390–400: завершён реальный повторный цикл одной единицы: первый loss/found→доставка3→REUSE2→новая отгрузка2→повторный loss/found1→доставка2. Same physicalkey, шесть исходных кодов, исходный FF3 и новый FF2 по одному разу, защищённый P20H20. SQL4.167/10.312/16.316ms: boundedPK retained, batchCASE-source ownerdelivery backlog.\n'),('wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md','\n390–399: true physical recurrent cycle completed; same unit loss/found→buyer→REUSE→new shipment→second loss/found→buyer. New order accepted2/unreceived0/history1-found1-net0; old FF3/new FF2 once, old6codes/rollback/replay. See recurrent_physical page. Grouped first-leg multi-SKU and aggregate lifecycle remain.\n')]:
 p=Path(filename);old=p.read_text(encoding='utf-8');out[filename]=entry+old if filename=='wiki/index.md' else old+entry
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');m=json.loads(p.read_text(encoding='utf-8'))
for x in m['increments']:
 if x['id']=='NI06.1':
  x.setdefault('implementedSlices',[]).append('390–399 real samephysicalkey recurrent loss/found after actual REUSE/newshipment; secondbuyer2/originalcodes/FFonce/rollback-replay')
  x['remainingScope']=[v for v in x.get('remainingScope',[]) if 'recurrent'not in v]
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+'\n'
p=Path('wiki/runbooks/nicora_active_work.md');t=p.read_text(encoding='utf-8').replace('Current native379/app373','Current native388/app373')
t=t.replace('Next: CASE-specific partialdispositions or groupedmultiSKU firstleg receiving;','Latest390–399: real samekey two physical loss/found cycles through actual REUSE and newshipment, secondbuyer2. Context398 fullydelivered; do notrerun intermediateP assertions.\n\nNext: groupedmultiSKU firstleg receiving;')
out[p.as_posix()]=t
root=next(Path('.').glob('*/NI08.1/178_container_cell_index.md')).parent.parent
out[(root/'NI06.1/400_recurrent_physical.md').as_posix()]='# Qwen390–399\nRead retained contexts and immutable facts only. Prove identical physicalkey2 belongs to two different confirmed loss events and recoveries, separated by actual STORE acceptance, REUSE receipt/putaway, new reservation/pick/load/depart. Originalbirth3/6codes unchanged; firstorderFF3once/newFF2once/customer2/history1-found1-net0. Do not rerun factories or intermediate availableP2 assertions. Exact command replay uses saved payload; actors restored/retired/protected20. No independent or hardware pass claimed.\n'
print(json.dumps(out))
