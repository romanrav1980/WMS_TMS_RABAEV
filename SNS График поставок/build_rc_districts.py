from pathlib import Path
import json,re,collections
root=Path(__file__).parent;p=root/'build_analysis.py';env={'__file__':str(p.resolve())};exec(p.read_text(encoding='utf8').split('trips={};details=')[0],env)
def norm(s):return re.sub(r'\s+',' ',(s or '').strip()).casefold().replace('ё','е')
groups=collections.defaultdict(set)
for chain,sheet in [('drinks','GFD'),('tobacco','ITMS')]:
 for r in env['read_sheet']('ГРАФИК ОТГРУЗКИ КЛИЕНТОВ.xlsx',sheet):
  if not r.get('G') or not r.get('D') or not r.get('E') or r['D']=='Наименование получателя':continue
  groups[(chain,norm(r['D']),norm(r['G']))].add((r['E'].strip(),r.get('F','').strip()))
source={k:next(iter(v)) for k,v in groups.items() if len(v)==1}
rules=[('Коломенский',r'коломн|парфентьев'),('Чеховский',r'чехов|лешино'),('Дмитровский',r'дмитров|габовск|шелепино'),('Солнечногорский',r'солнечногор|радумл|шелепанов'),('Пушкинский',r'пушкин'),('Лобненский',r'лобня|лобненск'),('Ногинский',r'ногинск|богородск|затишье'),('Раменский',r'раменск|софьино'),('Подольский',r'подольск|новоселки'),('Серпуховский',r'серпухов|всходы'),('Ленинский',r'видное|ленинский р-н'),('Красногорский',r'красногорск|ильинское-усово'),('Наро-Фоминский',r'наро-фомин|селятино|алабино'),('Домодедовский',r'домодедов'),('Одинцовский',r'одинцов'),('Истринский',r'истрин|истра'),('Мытищинский',r'мытищ'),('Щёлковский',r'щелков|щёлков'),('Балашихинский',r'балаших'),('Воскресенский',r'воскресенск'),('Ступинский',r'ступинск(ий р-н|ий район)|ступино г'),('Клинский',r'клинский р-н|клин г'),('Люберецкий',r'люберецк'),('Электростальский',r'электросталь')]
# Порядок для графика: Петербург, Москва, южное направление, затем восток.
city_order={name:i*100 for i,name in enumerate(['Санкт-Петербург','Москва','Тула','Калуга','Брянск','Орёл','Курск','Белгород','Воронеж','Липецк','Тамбов','Ростов-на-Дону','Краснодар','Волгоград','Астрахань','Нижний Новгород','Казань','Самара','Саратов','Пенза','Ульяновск','Уфа','Оренбург','Пермь','Ижевск','Екатеринбург','Челябинск','Тюмень','Курган','Омск','Новосибирск','Томск','Кемерово','Красноярск','Иркутск','Хабаровск','Владивосток'],1)}
records=json.loads((root/'data'/'october.json').read_text(encoding='utf8'))['records'];result={}
for r in records:
 if r['chain'] not in ('drinks','tobacco') or not r.get('receiver') or not r.get('address'):continue
 key=(r['chain'],norm(r['receiver']),norm(r['address']));address=r['address'];direct=source.get(key);city=(direct[0] if direct else r.get('destination','')).strip();district=(direct[1] if direct else '').strip();method='график отгрузки' if district else ''
 # Применяем адресные правила только к явному московскому региону или к зоне, обозначенной в данных как Москва.
 is_moscow=bool(re.search(r'московск(?:ая|ой|ую)\s*(?:обл|област)|\bмосква\b|^\s*(?:\d{6}\s*)?мо\s*[,\s]',address,re.I) or city.lower()=='москва')
 if not district and is_moscow:
  matches=[name for name,pattern in rules if re.search(pattern,address,re.I)]
  if len(matches)==1:district=matches[0];method='по адресу'
 result[key]={'chain':key[0],'receiver':key[1],'address':key[2],'city':'Москва' if is_moscow else city,'source_city':city,'district':district,'method':method,'moscow_region':is_moscow,'order':city_order.get('Москва' if is_moscow else city, 9000)}
(root/'data'/'rc_districts.json').write_text(json.dumps(list(result.values()),ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'addresses':len(result),'moscow_region':sum(x['moscow_region'] for x in result.values()),'moscow_assigned':sum(x['moscow_region'] and bool(x['district']) for x in result.values()),'source':sum(x['method']=='график отгрузки' for x in result.values()),'by_address':sum(x['method']=='по адресу' for x in result.values()),'ambiguous_source':sum(len(v)>1 for v in groups.values())},ensure_ascii=False))

# Расширяем районы явными данными адреса и включаем записи без адреса.
from enrich_address_districts import enrich
enrich()
