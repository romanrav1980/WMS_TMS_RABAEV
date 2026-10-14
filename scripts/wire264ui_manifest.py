from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('    <script src="admin-nav.js', '''<article class="panel" data-permission="customer_rule_edit">
<h2>Календарь магазина и исключения дат</h2>
<label>Склад <input id="storeCalWare" type="number" min="1"></label>
<label>Код магазина SAP/WMS <input id="storeCalStore" maxlength="100"></label>
<label>Дата доставки <input id="storeCalDate" type="date"></label>
<button id="storeCalRead">Прочитать дату</button>
<p>Недельный календарь применяется к новым заказам. Для конкретной даты можно записать открытие или закрытие.</p>
<label>Смещение от UTC, мин <input id="storeCalOffset" type="number" min="-720" max="840"></label>
<label>Дни доставки (1–7, через запятую) <input id="storeCalDays"></label>
<label><input id="storeCalSameDay" type="checkbox"> Разрешена отгрузка день в день</label>
<button id="storeCalConfigure">Сохранить недельный календарь</button>
<label>Исключение даты <select id="storeCalState"><option value="CLOSED">Закрыто</option><option value="OPEN">Открыто</option></select></label>
<input id="storeCalReference" maxlength="500" placeholder="Источник решения" aria-label="Источник решения календаря">
<input id="storeCalReason" maxlength="500" placeholder="Причина исключения" aria-label="Причина исключения даты">
<button id="storeCalPublish">Сохранить исключение даты</button>
<button id="storeCalRecover">Восстановить неподтверждённый запрос</button>
<p id="storeCalMessage" role="status"></p>
<p>Заказ на закрытую дату сохраняется в ожидании решения. Изменение календаря не допускает автоматически уже отложенные заказы.</p>
</article>
    <script src="admin-nav.js''')
s=s.replace('<script src="order-delivery.js"></script>','<script src="store-calendar.js"></script><script src="order-delivery.js"></script>');out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["packages"].append("RRL_STORE_CALENDAR_API")
j["components"]=[x.replace("../2026-10-10_ni081_workload_config/004_metadata_permission.sql","../2026-10-11_ni022_calendar/004_metadata_permission.sql")for x in j["components"]]
j["components"].append("../2026-10-11_ni022_calendar/002_api.sql")
j["additional_scripts"].append("../2026-10-11_ni022_calendar/003_guards.sql")
j["startup_scripts"].append("../2026-10-11_ni022_calendar/001_schema.sql")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
