from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
section='''<article class="panel" data-permission="customer_order_view">
<h2>Исходные заказы SAP и решения ERP</h2>
<label>Склад <input id="sapAdmissionWare" type="number" min="1" placeholder="Текущий доступный склад"></label>
<button id="sapAdmissionRefresh">Обновить источники</button>
<table><thead><tr><th>Заказ</th><th>Склад</th><th>Магазин</th><th>Доставка</th><th>Допуск</th><th>Состояние исполнения</th></tr></thead><tbody id="sapAdmissionRows"></tbody></table>
<p id="sapAdmissionDetail" role="status">Выберите источник SAP.</p>
<label>Хэш исходного содержания <input id="sapAdmissionHash" readonly style="width:100%"></label>
<h3>Исходная потребность SAP</h3><table><thead><tr><th>Артикул</th><th>Количество</th><th>Исходная единица</th></tr></thead><tbody id="sapAdmissionDemand"></tbody></table>
<p>Допуск и исполнение показываются отдельно от сохранённого результата первого импорта. Исходные количества и даты сохраняются.</p>
</article>
<article class="panel" data-permission="sap_store_decision_import">
<h2>Импорт XML-решения ERP</h2><input id="sapAdmissionXml" type="file" accept=".xml,application/xml">
<button id="sapAdmissionImport">Обработать исходное решение</button><p id="sapAdmissionImportMessage" role="status"></p>
<p>Файл содержит исходный Sender, MessageId, DecisionId, номер заказа, хэш, версию и решение. При потере ответа повторяется тот же файл.</p>
</article>'''
s=s.replace("</main>",section+"\n</main>",1).replace('<script src="store-calendar.js"></script>','<script src="sap-store-admission.js"></script><script src="store-calendar.js"></script>');out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["packages"].append("RRL_SAP_STORE_ADMISSION_API")
j["components"]=[x.replace("../2026-10-11_ni022_calendar/002_api.sql","../2026-10-11_ni022_admission/002_calendar.sql").replace("../2026-10-11_ni022_calendar/004_metadata_permission.sql","../2026-10-11_ni022_admission/005_metadata_permission.sql")for x in j["components"]]
j["components"].append("../2026-10-11_ni022_admission/003_api.sql")
j["additional_scripts"].append("../2026-10-11_ni022_admission/004_guards.sql")
j["startup_scripts"].append("../2026-10-11_ni022_admission/001_schema.sql")
j["startup_scripts"].append("../2026-10-11_ni022_admission/006_role.sql")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
