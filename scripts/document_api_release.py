from pathlib import Path
import ast,json,urllib.request,collections
root=Path.cwd();out=root/'wiki/components/api_reference_20261014';out.mkdir(parents=True,exist_ok=True)
index=['# Справочник Python методов и HTTP API','','[Назначение блоков](../../subprojects/nicora_system_reference.md)','','Описания методов ниже берутся из docstring, а если его нет — это прямо отмечено. Сигнатура, исходник и вызываемые методы позволяют проследить реализацию без выдуманной семантики. Статические вызовы не доказывают выполнение ветки при каждом запросе.','']
base=root/'api/wms_api_server/app';groups=collections.defaultdict(list)
for path in sorted(base.rglob('*.py')):
 if '__pycache__' in path.parts:continue
 rel=path.relative_to(root).as_posix();tree=ast.parse(path.read_text(encoding='utf-8-sig'))
 module=path.relative_to(base).parts
 group=module[1] if module[0]=='modules' and len(module)>1 else module[0]
 for n in ast.walk(tree):
  if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
  sig=ast.unparse(n.args);doc=ast.get_docstring(n) or 'Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.'
  calls=sorted({ast.unparse(x.func) for x in ast.walk(n) if isinstance(x,ast.Call)})
  groups[group].append('\n'.join(['### '+n.name,'','[Исходник: '+rel+':'+str(n.lineno)+'](../../../'+rel+'#L'+str(n.lineno)+')','','```python',n.name+'('+sig+')'+(' -> '+ast.unparse(n.returns) if n.returns else ''),'```','',doc,'','Вызывает: '+', '.join('`'+v+'`' for v in calls[:35])+(' (остальные вызовы — в исходнике)' if len(calls)>35 else ''), '']))
for group,entries in sorted(groups.items()):
 name=group.replace('.','_')+'.md';(out/name).write_text('# Методы: '+group+'\n\n'+'\n'.join(entries),encoding='utf-8');index.append('- ['+group+']('+name+') — '+str(len(entries))+' методов.')
try:
 with urllib.request.urlopen('http://127.0.0.1:8088/openapi.json',timeout=30) as r:api=json.load(r)
 (out/'openapi.json').write_text(json.dumps(api,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# HTTP API: опубликованные маршруты','','Источник: OpenAPI работающего API на дату выпуска. Полные request/response schemas, required поля и ссылки — в [openapi.json](openapi.json). Авторизация и предметные права дополнительно проверяются серверными зависимостями; наличие маршрута не предоставляет право.','','| Метод | Путь | Назначение / summary | operationId |','|---|---|---|---|']
 for path,methods in api['paths'].items():
  for method,op in methods.items():
   if method not in ('get','post','put','patch','delete','options','head'):continue
   lines.append('| '+method.upper()+' | `'+path+'` | '+op.get('summary','').replace('|','\\|')+' | '+op.get('operationId','')+' |')
 (out/'http_routes.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');index+=['','[HTTP маршруты](http_routes.md) · [OpenAPI схемы](openapi.json)']
except Exception as e:raise RuntimeError('Cannot capture live OpenAPI: '+type(e).__name__) from None
(out/'README.md').write_text('\n'.join(index)+'\n',encoding='utf-8');print('Documented methods',sum(map(len,groups.values())))
