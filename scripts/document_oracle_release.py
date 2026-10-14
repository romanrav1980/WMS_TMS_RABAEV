"""Generate a linked Oracle reference from dictionary metadata and source."""
import collections,json,re,sys
from urllib.parse import quote
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wiki/database/release_20261014'
load_local_oracle_environment();sys.path.insert(0,str(ROOT/'api/wms_api_server'))
from app.config import get_settings
s=get_settings()
for d in ['tables','programs']:(OUT/d).mkdir(parents=True,exist_ok=True)
def cell(v):
 text=str(v or '')
 if '\ufffd' in text:return 'Исходный комментарий Oracle содержит повреждённые символы; описание требует уточнения.'
 return text.replace('|','\\|').replace('\n',' ')
def domain(name):
 for token,label in [('STOCK','Единое ядро остатков, резервов и проводок'),('TRACE','Маркировка и агрегация'),('TT','Рейсы и транспорт'),('TRANSPORT','Транспортное планирование'),('STORE','Доставка и приёмка магазина'),('IW','Межскладское перемещение'),('INTERWARE','Межскладское перемещение'),('TARE','Оборотная тара'),('RETURN','Возвраты'),('PICK','Отбор и волны'),('CASE','Сборка CASE'),('HU','Грузовые единицы и вложенность'),('QC','Контроль качества'),('QUALITY','Контроль качества'),('SAP','Интеграция SAP'),('INVOICE','Счета'),('COST','Затраты'),('RESOURCE','Персонал и техника'),('VEHICLE','Транспортные средства'),('WAREHOUSE','Складские задания и топология'),('RECEIPT','Приёмка'),('REGULATORY','Регуляторный обмен'),('PRODUCTION','Производство'),('OUTBOX','Исходящие сообщения')]:
  if token in name.split('_'):return label
 return 'Legacy / общие справочники; бизнес-назначение требует уточнения по вызывающему коду'
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.arraysize=1000
 q.execute("select table_name,column_name,data_type,data_length,data_precision,data_scale,nullable from user_tab_columns order by table_name,column_id")
 cols=collections.defaultdict(list)
 for r in q:cols[r[0]].append(r[1:])
 q.execute('select table_name,comments from user_tab_comments');comments=dict(q.fetchall())
 q.execute('select table_name,column_name,comments from user_col_comments');cc={(t,n):v for t,n,v in q}
 q.execute('select table_name,constraint_name,constraint_type,r_constraint_name,status from user_constraints order by table_name,constraint_name')
 constraints=collections.defaultdict(list)
 for r in q:constraints[r[0]].append(r[1:])
 q.execute('select constraint_name,column_name from user_cons_columns order by constraint_name,position');keys=collections.defaultdict(list)
 for n,col in q:keys[n].append(col)
 q.execute('select constraint_name,table_name from user_constraints');targets=dict(q.fetchall())
 q.execute("select name,type,referenced_name,referenced_type from user_dependencies where referenced_owner='RABAEV' order by name,referenced_name")
 deps=collections.defaultdict(set);callers=collections.defaultdict(set)
 for n,t,r,rt in q:deps[n].add(r);callers[r].add(n)
 q.execute('select object_name,package_name,argument_name,position,data_type,in_out,defaulted,overload from user_arguments order by package_name,object_name,subprogram_id,sequence')
 args=collections.defaultdict(list)
 for n,p,*r in q:args[p or n].append((n,*r))
 q.execute('select name,type,text from user_source order by type,name,line');src=collections.defaultdict(list)
 for n,t,line in q:src[(t,n)].append(line)
 q.execute("select object_type,object_name from user_objects where (object_name not like 'BIN$%' or object_name in (select trigger_name from user_triggers where table_name not like 'BIN$%')) and object_type not in ('LOB','INDEX','PACKAGE BODY','SEQUENCE') order by object_type,object_name")
 objects=q.fetchall();paths={n:('tables/' if t=='TABLE' else 'programs/')+re.sub(r'[^A-Za-z0-9_.-]','_',n)+'.md' for t,n in objects}
 def links(names):return ', '.join('['+n+'](../'+paths[n]+')' if n in paths else '`'+n+'`' for n in sorted(names)) or 'Нет зарегистрированных зависимостей.'
 index=['# Каталог Oracle RABAEV — 14.10.2026','','Источник: живой Oracle, USER_TAB_COLUMNS / USER_CONSTRAINTS / USER_ARGUMENTS / USER_DEPENDENCIES / USER_SOURCE. Это техническая справка; классификация по имени помечена отдельно от подтверждённого бизнес-описания. Динамический SQL не полностью отражается в USER_DEPENDENCIES.','','[Работа системы и назначение ключевых объектов](../../subprojects/retailcase_system_reference.md) · [Установка](../../../db/releases/2026-10-14/README.md)','','| Тип | Объект | Подсистема (классификация по имени) |','|---|---|---|']
 for t,n in objects:
  index.append('| '+t+' | ['+n+']('+paths[n]+') | '+domain(n)+' |')
  page=['# '+n,'','Тип: **'+t+'**. Схема: `RABAEV`.','','Подсистема по имени: '+domain(n)+'.','']
  if t=='TABLE':
   page+=['Описание Oracle: '+(cell(comments.get(n)) or 'Не задано; не следует выводить точное бизнес-назначение только из имени.') ,'','## Поля','','| Поле | Тип | NULL | Комментарий |','|---|---|---|---|']
   for col,dt,length,precision,scale,nullable in cols[n]:
    typ=dt+(f'({precision},{scale or 0})' if precision else f'({length} bytes)' if 'CHAR' in dt or dt=='RAW' else '')
    display_col=col.encode('unicode_escape').decode('ascii') if '\ufffd' in col else col
    page.append('| `'+display_col+'` | '+typ+' | '+nullable+' | '+cell(cc.get((n,col)))+' |')
   page+=['','## Ограничения и связи','','| Ограничение | Тип | Поля | Ссылка | Статус |','|---|---|---|---|---|']
   for con,ct,ref,status in constraints[n]:page.append('| '+con+' | '+ct+' | '+', '.join(keys[con])+' | '+(targets.get(ref,'')+' ('+', '.join(keys[ref])+')' if ref else '')+' | '+status+' |')
   page+=['','P — первичный ключ, U — уникальность, R — внешний ключ, C — CHECK/NOT NULL. Точные CHECK-выражения, defaults и индексы находятся в SQL-снимке.']
  else:
   page+=['## Интерфейс','','| Подпрограмма | Аргумент (пустой = RETURN) | Позиция | Тип | Направление | Default | Overload |','|---|---|---|---|---|---|---|']
   for row in args[n]:page.append('| '+' | '.join(cell(x) for x in row)+' |')
   source=''.join(src.get((t,n),[])+src.get(('PACKAGE BODY',n),[]))
   touched=sorted(set(re.findall(r'\b(?:insert\s+into|update|delete\s+from|merge\s+into)\s+(RRL_[A-Z0-9_]+)',source,re.I)))
   page+=['','## Потенциальные записи по тексту SQL','',''+links([v.upper() for v in touched]),'','Это статический указатель, а не гарантия выполнения записи при каждом вызове. Полная семантика и транзакционные условия — в теле программы.']
  page+=['','## Зависимости','',''+links(deps[n]),'','## Кто использует','',''+links(callers[n]),'','## Исходный код','','[Полный SQL-снимок](../../../../db/releases/2026-10-14/README.md). Ищите точное имя `'+n+'` в файле соответствующего типа.','']
  (OUT/paths[n]).write_text('\n'.join(page),encoding='utf-8')
 (OUT/'README.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
 print('Generated reference pages:',len(objects))
