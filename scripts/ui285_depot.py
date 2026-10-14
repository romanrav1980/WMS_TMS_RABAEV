from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouses.html");s=p.read_text(encoding="utf-8")
panel="""<section class="panel" data-permission="warehouse_settings_edit"><h2>Адрес отправления транспорта со склада</h2>
<label>Склад<input id="wdWare" inputmode="numeric"></label><button id="wdRead">Прочитать настройки адреса</button>
<label>Код существующего адреса<input id="wdAddress" maxlength="200"></label><p>Адрес должен иметь координаты в справочнике. Пустое значение отменяет настройку, сохраняя историю.</p>
<label>Основание изменения<textarea id="wdReason" maxlength="500"></textarea></label>
<button id="wdSave" disabled>Сохранить адрес отправления</button><button id="wdRetry" disabled>Повторить сохранённую команду</button>
<button id="wdResolve" disabled>Проверить исход</button><p id="wdPending" role="status"></p><p id="wdMessage" role="status"></p></section>"""
s=s.replace("</main>",panel+"</main>").replace("</body>",'<script src="warehouse-depot.js"></script></body>');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouses.js");s=p.read_text(encoding="utf-8").replace("function selectWarehouse(warehouse) {","function selectWarehouse(warehouse) {\n  window.dispatchEvent(new CustomEvent('warehouse-depot-selected',{detail:{warehouse_id:warehouse.id}}));",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
