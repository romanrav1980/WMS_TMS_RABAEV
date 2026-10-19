"""Build the static RETAILCASE operations guide; no live data exported."""
from pathlib import Path
import json
import shutil
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(__file__).resolve().parent
CATALOG = ROOT / 'coordination/retailcase-claude/proposals/C0049/role_catalog.json'

ROLE_PROCESSES = {
 'logistics_director':'transport readiness consolidation delivery store close',
 'dc_director':'readiness pick quality consolidation loading close shift',
 'transport_director':'transport delivery returns close',
 'wh_ops_head':'master readiness replenishment pick quality loading shift',
 'shift_supervisor':'readiness replenishment pick quality consolidation loading shortage shift',
 'lead_receiving':'inbound storage shift','lead_storage':'storage replenishment readiness shortage shift',
 'lead_picking':'pick readiness shortage shift','lead_qc':'quality shortage returns',
 'lead_expedition':'consolidation loading shift','sap_doc_operator':'orders integration shortage',
 'mdm_specialist':'orders master','wave_planner':'readiness replenishment transport',
 'receiving_operator':'inbound storage returns','reach_driver':'storage replenishment',
 'forklift_driver':'storage consolidation loading','picker':'pick shortage shift',
 'qc_controller':'quality returns','loader':'loading consolidation','stock_controller':'count shortage storage',
 'inventory_auditor':'count shortage','returns_specialist':'returns quality shortage',
 'tare_owner':'returns delivery close','crossdock_head':'consolidation inbound loading',
 'transport_planning_head':'transport delivery loading close','route_planner':'transport readiness delivery',
 'dispatcher':'transport loading delivery store','yard_coordinator':'loading transport','driver':'delivery loading store returns',
 'fleet_manager':'transport shift','carrier_manager':'transport delivery close','region_manager':'store delivery returns',
 'store_director':'store delivery returns','store_receiver':'store returns',
 'billing_economist':'close transport','cost_approver':'close','analyst':'close delivery store pick',
 'access_admin':'shift integration','integration_specialist':'integration orders store','auditor_ro':'close count quality integration',
 'knowledge_editor':'shift integration','warehouse_technologist':'master storage replenishment quality',
 'consolidation_coordinator':'transport consolidation quality loading'
}
ROLE_SCREENS = {
 'logistics_director':'director kpi dispatch','dc_director':'director shift kpi',
 'transport_director':'dispatch planner kpi tare','wh_ops_head':'shift storage master',
 'shift_supervisor':'shift wave shortage','lead_receiving':'receiving tasks','lead_storage':'storage tasks reach',
 'lead_picking':'shift picker shortage','lead_qc':'quality hu shortage','lead_expedition':'consolidation loading hu',
 'sap_doc_operator':'orders integration','mdm_specialist':'master orders','wave_planner':'shift wave orders',
 'receiving_operator':'receiving hu tasks','reach_driver':'reach tasks','forklift_driver':'tasks loading',
 'picker':'picker assembly','qc_controller':'quality hu','loader':'loading hu','stock_controller':'shortage count hu',
 'inventory_auditor':'count tasks','returns_specialist':'returns quality','tare_owner':'tare returns',
 'crossdock_head':'consolidation receiving hu','transport_planning_head':'planner dispatch kpi',
 'route_planner':'planner dispatch','dispatcher':'dispatch loading driver','yard_coordinator':'dispatch loading',
 'driver':'driver tare','fleet_manager':'planner master','carrier_manager':'dispatch finance','region_manager':'kpi store',
 'store_director':'store returns','store_receiver':'store','billing_economist':'finance kpi','cost_approver':'finance',
 'analyst':'kpi director','access_admin':'access integration','integration_specialist':'integration',
 'auditor_ro':'integration kpi','knowledge_editor':'knowledge','warehouse_technologist':'master storage',
 'consolidation_coordinator':'consolidation hu loading'
}

def neutral(value):
    if not isinstance(value,str): return value
    value=value.replace('SAP','ERP').replace('BLC','владелец торгового процесса')
    value=re.sub(r'\([^)]*_[^)]*\)', '', value)
    value=re.sub(r'\b(?:OBJECT|PERSON)\s*(?:\(native\))?\s*:\s*', '', value)
    return value.strip()

catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
roles=[]
for raw in catalog['roles']:
    role={k:raw.get(k) for k in ('id','title','family','reports_to','scope','devices','resp','not_resp','decisions','sod','handover','escalate','shift','ui','scenarios')}
    for key in ('title','handover','escalate','shift'): role[key]=neutral(role.get(key))
    for key in ('resp','not_resp','decisions','sod'): role[key]=[neutral(v) for v in (role.get(key) or [])]
    role['processes']=ROLE_PROCESSES[raw['id']].split()
    role['screens']=ROLE_SCREENS[raw['id']].split()
    # Historical UI/scenarios are explicitly displayed as a project, never as current acceptance.
    role['ui']={k:neutral(v) for k,v in raw.get('ui',{}).items()}
    role['scenarios']=[{k:neutral(v) for k,v in s.items()} for s in raw.get('scenarios',[])]
    role['catalog_status']=raw['workspace']
    roles.append(role)

extra=[
 dict(id='warehouse_technologist',title='Технолог склада и слоттинга',family='warehouse_ops',reports_to='wh_ops_head',scope='WAREHOUSE',devices=['desktop','tablet'],
      resp=['Определять допустимые зоны, адреса, упаковку и вместимость.','Разбирать отсутствие пригодного адреса и несовместимость условий хранения.','Согласовывать версии правил с эксплуатацией и владельцем справочников.'],
      decisions=['Предложить новую версию размещения и передать её на утверждение.']),
 dict(id='consolidation_coordinator',title='Координатор транспортной консолидации',family='warehouse_ops',reports_to='crossdock_head',scope='DC',devices=['desktop','tablet'],
      resp=['Сопоставлять все ожидаемые части одного магазина с фактически принятыми.','Поддерживать дерево мест и обратный график к финальному рейсу.','Проверять полноту, QC, температурную совместимость и готовность к погрузке.'],
      decisions=['Передать готовый состав экспедиции.','Эскалировать опаздывающий источник и согласовать изменение плана.'])]
for r in extra:
    r.update(not_resp=['Не подменяет физический факт плановым статусом.'],sod=['Права по назначению; независимый контроль выполняет контролёр.'],
             handover='Объекты, версии, подтверждённые факты, блокировки и сроки.',escalate='Руководителю операции; при угрозе рейсу также диспетчеру.',
             shift='По операционному графику площадки.',ui={'first':'Разрешённая область, ожидаемое и фактическое состояние, открытые блокировки.'},scenarios=[],
             processes=ROLE_PROCESSES[r['id']].split(),screens=ROLE_SCREENS[r['id']].split(),catalog_status='extension')
    roles.append(r)

for r in roles:
    if r['id']=='logistics_director': r['reports_to']='executive'
    if r['id']=='region_manager': r['reports_to']='retail_director'
    if r['id'] in ('access_admin','integration_specialist'): r['reports_to']='it_director'
    if r['id'] in ('billing_economist','cost_approver'): r['reports_to']='finance_director'
    if r['id']=='auditor_ro': r['reports_to']='audit_owner'
    if r['id']=='knowledge_editor': r['reports_to']='wh_ops_head'
    if r['id']=='sap_doc_operator': r['title']='Оператор ERP и документов'
    if r['id']=='analyst':
        r['resp']=['Проверять источники, полноту и расшифровку согласованных KPI V2.','Готовить предложения новых метрик отдельно от утверждённых паспортов.']
        r['scenarios']=[]
    r['coordination']={
      'region_manager':'Административная линия — розница; с логистикой согласует поставки и риски.',
      'driver':'Оперативно — диспетчер рейса; административно — работодатель или перевозчик.',
      'store_receiver':'Подчиняется управляющему магазина; взаимодействует с водителем и диспетчером.',
      'lead_qc':'Административно — смена; функциональная независимость качества сохраняется.',
      'qc_controller':'Результат контроля независим от сборщика; подчинение не разрешает обход QC.',
      'billing_economist':'Финансовая вертикаль; операционные основания предоставляет транспорт.',
      'cost_approver':'Финансовая вертикаль; согласующий независим от автора расхода.',
      'access_admin':'ИТ-вертикаль; бизнес-владелец согласует мандат, администратор оформляет назначение.'
    }.get(r['id'],'Передача результата соседнему участнику не меняет административного подчинения.')

assets={
 'director':('reports/retailcase/2026-10-14/claude/C0056/block4/screenshots/w1_director_desktop.png','Директор РЦ: процессы и схема склада','Архивная проверка 14–15.10.2026; счётчики — выборка, не сетевой KPI.'),
 'dispatch':('reports/retailcase/2026-10-14/claude/C0056/block4/screenshots/w3_dispatcher_desktop.png','Диспетчер: рейсы, ворота, машины','Архивная проверка интерфейса; это не текущие рейсы.'),
 'shift':('reports/retailcase/2026-10-17/claude/C0124/screenshots/p1_path_1440.png','Старший смены: волна → риски → ресурсы','Проверка навигации 17.10.2026; локальные данные, не учебный рейс из атласа.'),
 'storage':('reports/retailcase/2026-10-15/claude/C0074/block3/screenshots/t1_storage.png','Хранение и ричтраки','Архивная проверка 15.10.2026; снимок не подтверждает физическую работу техники.'),
 'receiving':('reports/retailcase/2026-10-15/claude/C0074/block4/screenshots/r1_receiving.png','Приёмка склада','Архивная проверка 15.10.2026.'),
 'picker':('reports/retailcase/2026-10-14/claude/C0056/block4/screenshots/w4_picker_tsd.png','Комплектовщик: обзор задания','Архивная карточка; физический отбор выполняется в терминальном экране.'),
 'store':('reports/retailcase/2026-10-17/product-flow/store-ui/store-list-390.png','Приложение магазина','Локальная проверка 17.10.2026: CASE1154, рейс 33659, приёмка 25EA.'),
 'act':('reports/retailcase/2026-10-17/product-flow/store-ui/store-act-390.png','Сохранённый акт магазина','Архивный акт локальной проверки; не документ учебного маршрута.'),
 'kpi':('reports/retailcase/2026-10-17/kpi-v2/product-ui-compiled/scoped-v2-desktop.png','KPI V2','Собранный интерфейс 17.10.2026; только подтверждённые наблюдения.')}
images={}
(SITE/'assets').mkdir(parents=True,exist_ok=True)
for key,(source,title,caption) in assets.items():
    path=ROOT/source
    if not path.is_file(): raise FileNotFoundError(path)
    shutil.copyfile(path,SITE/'assets'/(key+'.png'))
    images[key]=dict(src='assets/'+key+'.png',title=title,caption=caption,source=source)

data=dict(version='2.0',date='19.10.2026',roles=roles,families=catalog['families'],images=images,
 roots={'executive':'Генеральный директор / владелец бизнеса','retail_director':'Директор розницы','it_director':'Руководитель ИТ','finance_director':'Финансовый директор','audit_owner':'Независимый контроль / собственник'})
(SITE/'data.js').write_text('window.GUIDE = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print(f'Built {len(roles)} role instructions and {len(images)} archived screenshots')
