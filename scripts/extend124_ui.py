from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.html")
s=p.read_text(encoding="utf-8")
section="""<section class="panel" data-permission="stock_inventory_count"><h2>Регистрация найденной маркированной паллеты</h2><p>Используйте действующую ревизию склада. Состав отправителя должен относиться к этой ревизии, паллете и товару.</p><label>Документ состава<input id="tmManifest" maxlength="100"></label><label>Ревизия склада<input id="tmRevision" inputmode="numeric"></label><label>Идентификатор паллеты, скан<input id="tmPallet" maxlength="50"></label><label>Ячейка, скан<input id="tmCell" maxlength="60"></label><label>Артикул<input id="tmArticle" maxlength="160"></label><label>Фактическое количество в базовой единице<input id="tmQty" inputmode="decimal"></label><label>Срок годности<input id="tmExpiry" type="date"></label><label>Учётная цена<input id="tmPrice" inputmode="decimal" value="0"></label><label>Основание<input id="tmReason" maxlength="1000"></label><label>Сканированные агрегации по профилям<textarea id="tmScans" rows="5" placeholder='[{"system_code":"CRPT","profile_code":"TOBACCO","level":"PALLET","code":"код со сканера"}]'></textarea></label><button id="tmBirth">Подтвердить фактический товар</button><p>Все обязательные профили должны подтверждать одни и те же физические единицы. Количество разных систем маркировки не суммируется.</p></section>"""
s=s.replace('<button id="tmImport">',section+'<button id="tmImport">',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.js");s=p.read_text(encoding="utf-8")
s=s.replace('for(const id of ["tmFile","tmRaw","tmWare","tmLoad","tmImport"])el(id).disabled=busy||!!pending;','document.querySelectorAll("main input,main textarea,main button").forEach(n=>n.disabled=busy||!!pending);')
s=s.replace('base()+"/api/inventory/trace-manifests"+path','base()+path')
s=s.replace('request("",pending.body)','request(pending.path,pending.body)')
s=s.replace('say("Состав сохранён. Остаток не изменён.");','say(result.stock_changed===false?"Состав сохранён. Остаток не изменён.":"Операция подтверждена системой.");')
s=s.replace('request("/warehouses/"+ware)','request("/api/inventory/trace-manifests/warehouses/"+ware)')
s=s.replace('pending={body:{operation_id:','pending={path:"/api/inventory/trace-manifests",body:{operation_id:')
needle=' el("tmLoad").addEventListener("click",load);'
birth=""" el("tmBirth").addEventListener("click",()=>{if(busy||pending)return;try{const revision=Number(el("tmRevision").value);if(!Number.isSafeInteger(revision)||revision<1)throw Error("Укажите действующую ревизию.");const aggregations=JSON.parse(el("tmScans").value);if(!Array.isArray(aggregations)||!aggregations.length)throw Error("Укажите сканы обязательных агрегаций.");const body={operation_id:"TRACE.BIRTH:"+crypto.randomUUID(),revision_id:revision,uid:el("tmPallet").value,cell:el("tmCell").value,article:el("tmArticle").value,quantity:el("tmQty").value,expiry_date:el("tmExpiry").value,price:el("tmPrice").value,reason:el("tmReason").value,capture:{manifest_operation_id:el("tmManifest").value,units:[],aggregations}};pending={path:"/api/inventory/stock-posting/inventory/lots",body,confirmed:false};localStorage.setItem(key(),JSON.stringify(pending));send();}catch(e){pending=null;say(e.message);controls();}});
"""
assert needle in s;s=s.replace(needle,birth+needle)
s=s.replace('if(pending)el("tmRaw").value=pending.body.manifest_json;','if(pending?.body.manifest_json)el("tmRaw").value=pending.body.manifest_json;')
s=s.replace('identity=current;++epoch;busy=false;pending=null;','identity=current;++epoch;busy=false;pending=null;for(const id of ["tmManifest","tmRevision","tmPallet","tmCell","tmArticle","tmQty","tmExpiry","tmReason","tmScans"])el(id).value="";')
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
