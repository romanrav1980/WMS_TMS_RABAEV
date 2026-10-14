from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
panel='''<section class="panel" data-permission="customer_order_import" id="sapAutoPreparation">
<h2>Автоматическая подготовка СТ</h2>
<p>Состав рассчитывается по целым коробкам, нормам товара и порядку комплектования. Остатки меняются при исполнении складских заданий.</p>
<div class="inline-form">
<label>Исходный заказ SAP <input id="sapAutoOrder" inputmode="numeric"></label>
<label>Масса товара на место, кг <input id="sapAutoMass" inputmode="decimal" placeholder="Укажите предел"></label>
<label>Объём товара на место, м³ <input id="sapAutoVolume" inputmode="decimal" placeholder="Укажите предел"></label>
<label>Максимум мест <input id="sapAutoCount" inputmode="numeric" value="100"></label>
</div>
<p>Пределы относятся к товару. Учитывайте грузоподъёмность тары при их выборе. Расчёт объёма не подтверждает геометрию укладки.</p>
<button id="sapAutoRead">Рассчитать состав</button>
<table class="rights-table"><thead><tr><th>Место</th><th>Группа</th><th>Товар</th><th>Базовое количество</th><th>Масса места, кг</th><th>Объём места, м³</th></tr></thead><tbody id="sapAutoRows"></tbody></table>
<button id="sapAutoSave" disabled>Подготовить СТ по предложению</button>
<button id="sapAutoRetry" disabled>Повторить сохранённый запрос</button>
<button id="sapAutoResolve" disabled>Проверить исход запроса</button>
<p id="sapAutoPending" role="status"></p><p id="sapAutoMessage" role="status"></p>
</section>
'''
s=s.replace('<section class="panel" data-permission="customer_order_import"><h2>Укладка исходного заказа SAP',panel+'<section class="panel" data-permission="customer_order_import"><h2>Укладка исходного заказа SAP')
s=s.replace('<script src="sap-preparation-layout.js"></script>','<script src="wave-command-intent.js?v=20261013-890"></script><script src="sap-preparation-layout.js?v=20261013-1115"></script><script src="sap-automatic-preparation.js?v=20261013-1115"></script>')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-preparation-layout.js");s=p.read_text(encoding="utf-8")
s=s.replace(" const pending=()=>", " const autoPending=()=>!!localStorage.getItem('sap-auto-preparation:'+auth().state.apiBase+':'+auth().state.user?.username);\n const pending=()=>")
s=s.replace("busy||!proposal||!!p","busy||!proposal||!!p||autoPending()")
s=s.replace("try{command=pending();", "try{if(autoPending())throw Error('Сначала выясните исход автоматической подготовки.');command=pending();")
s=s.replace("localStorage.removeItem(key());proposal=null;", "localStorage.removeItem(key());window.dispatchEvent(new Event('sap-manual-preparation-settled'));proposal=null;")
s=s.replace(" controls();\n})();"," window.addEventListener('storage',controls);window.addEventListener('sap-auto-preparation-settled',controls);\n controls();\n})();")
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py");s=p.read_text(encoding="utf-8").replace("from ..domain.automatic_layout import STRATEGY\n","")
s=s.replace("def auto_call(method", "import oracledb\n\ndef auto_call(method")
s=s.replace('        raise HTTPException(409, str(exc)) from exc\n\n@router.post', '        raise HTTPException(409, str(exc)) from exc\n    except oracledb.DatabaseError as exc:\n        if getattr(exc.args[0], "code", 0) in (54, 60, 30006):\n            raise HTTPException(409, "AUTO_PREPARATION_RESOURCE_BUSY_RETRY_SAVED_REQUEST") from exc\n        raise\n\n@router.post',1)
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace("then 1 else 0 end\n", "then 1 else 0 end,s.PICKING_FINISH_AT,c.SHIPMENT_DATE\n")
s=s.replace("map_id,future=header","map_id,future,finish,shipment=header")
s=s.replace('"stock_changed":False,"automatic_split_verified":False}', '"picking_finish_at":finish.isoformat() if finish else None,\n            "shipment_at":shipment.isoformat() if shipment else None,\n            "stock_changed":False,"automatic_split_verified":False}')
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py");s=p.read_text(encoding="utf-8").replace('not getattr(cur, "_auto_write_snapshot", False)','True')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
