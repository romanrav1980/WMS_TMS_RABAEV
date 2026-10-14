from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
panel="""<section class="panel" data-permission="customer_order_import"><h2>Укладка исходного заказа SAP в прежнюю СТ</h2>
<label>Номер исходного заказа<input id="splOrder" inputmode="numeric"></label><button id="splRead">Предложить по норме товара</button>
<table><thead><tr><th>Товар</th><th>Норма на паллету</th><th>Вложенность коробки</th><th>Число паллет</th></tr></thead><tbody id="splArticleRows"></tbody></table>
<button id="splRecalculate">Пересчитать с выбранным числом паллет</button>
<table><thead><tr><th>Паллета</th><th>Товар</th><th>Количество в базовых единицах</th></tr></thead><tbody id="splPalletRows"></tbody></table>
<button id="splSave" disabled>Подготовить прежнюю СТ</button><button id="splRetry" disabled>Повторить сохранённую команду</button>
<p id="splPending" role="status"></p><p id="splMessage" role="status"></p></section>"""
s=s.replace("</main>",panel+"</main>").replace("</body>",'<script src="sap-preparation-layout.js"></script></body>');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sap-store-admission.js");s=p.read_text(encoding="utf-8")
s=s.replace("      el('sapAdmissionHash').value=value.content_hash;","      window.dispatchEvent(new CustomEvent('sap-store-source-selected',{detail:{order_id:id}}));\n      el('sapAdmissionHash').value=value.content_hash;");out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
