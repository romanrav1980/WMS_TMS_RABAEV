from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<body class="auth-pending"','<body class="auth-pending order-workspace-page"')
marker='</section></main>'
assert s.count(marker)==1
panel='''</section><section class="panel order-picking-panel" id="orderWavePlanning" data-permission="pick_wave_view">
<h2>Волна складского исполнения</h2>
<p>Включите обеспеченный план в волну, рассчитайте её и проверьте задания перед запуском.</p>
<label>План заказа<select id="opWavePlan" title="Выбрать существующий обеспеченный план этого заказа"></select></label>
<label>Волна склада<select id="opWaveSelect" title="Выбрать существующую волну склада заказа"></select></label>
<button id="opWaveRead" title="Прочитать последние100 волн выбранного склада">Показать волны</button>
<label>Название новой волны<input id="opWaveName" maxlength="255" title="Название для создания новой волны на складе заказа"></label>
<button id="opWaveCreate" data-permission="pick_wave_create" title="Создать волну без автоматического выпуска заданий">Создать волну</button>
<button id="opWaveAdd" data-permission="pick_wave_create" title="Включить план в выбранную волну прежним механизмом WMS">Включить план</button>
<button id="opWaveCalculate" data-permission="pick_wave_calculate" title="Рассчитать задания и готовность выбранной волны">Рассчитать волну</button>
<button id="opWaveLaunch" data-permission="pick_wave_launch" title="Запустить рассчитанную волну через действующее ядро">Запустить волну</button>
<button id="opWaveRetry" title="Проверить исход создания либо продолжить сохранённое действие">Продолжить сохранённое действие</button>
<p id="opWaveStatus" role="status"></p>
<a id="opWaveOpen" hidden title="Открыть состав, готовность, задания и исполнение выбранной волны">Открыть складское исполнение →</a>
</section></main>'''
s=s.replace(marker,panel).replace('</body>','<script src="order-wave-planning.js"></script></body>');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.js");s=p.read_text(encoding="utf-8")
a='  order=detail;plans=list.filter(p=>p.customer_order_id===id);'
assert s.count(a)==1
s=s.replace(a,a+'\n  window.dispatchEvent(new CustomEvent("wms-order-plans-read",{detail:{order:detail,plans}}));');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.css");s=p.read_text(encoding="utf-8")
s+='''\n.order-picking-panel #opWaveStatus{flex-basis:100%;background:#f1f5f9;border-radius:10px;padding:12px;line-height:1.5}
.order-picking-panel input{min-height:44px;padding:10px;border:1px solid #cad6e5;border-radius:9px}
@media(max-width:1279px){body.order-workspace-page{min-width:0}.order-workspace-page .app{grid-template-columns:minmax(0,1fr)}.order-workspace-page .sidebar{display:none}.order-workspace-page .workspace{min-width:0;width:100%}.order-workspace-page .panel{max-width:100%;overflow-x:auto}.order-workspace-page .topbar{height:auto;flex-wrap:wrap;gap:12px;padding:16px}.order-workspace-page .top-actions{flex-wrap:wrap}.order-workspace-page .search{max-width:100%}.order-workspace-page .breadcrumbs{font-size:16px}.order-picking-panel>*{max-width:100%;min-width:0}.order-picking-panel .rights-table-wrap{overflow:auto}}
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
