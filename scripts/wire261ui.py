from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/receiving.html");s=p.read_text(encoding="utf-8").replace('<p id="receiptSuggestion">','''<section aria-label="План укладки поставки">
<h3>Предложение укладки оставшегося количества</h3>
<label>Количество паллет <input id="receiptLayoutCount" type="number" min="1" max="200" placeholder="По норме товара"></label>
<label>Шаг количества <input id="receiptLayoutStep" inputmode="decimal" placeholder="Необязательно"></label>
<label>Свой план: количество каждой паллеты с новой строки
<textarea id="receiptLayoutAmounts" rows="3" placeholder="Оставьте пустым для распределения по количеству паллет"></textarea></label>
<button id="receiptLayoutPreview" type="button">Рассчитать предложение</button>
<p id="receiptLayoutMessage" role="status">Выберите строку товара.</p>
<table><thead><tr><th>Паллета</th><th>Количество</th><th>Единица</th><th>Примечание</th></tr></thead><tbody id="receiptLayoutRows"></tbody></table>
</section>
<p id="receiptSuggestion">''')
s=s.replace('<script src="receiving.js"></script>','<script src="receiving-layout.js"></script><script src="receiving.js"></script>');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8").replace('state.policy=policy;el(\'receiptMarking\')','window.dispatchEvent(new CustomEvent("wms-receipt-line-selected", {detail:line}));\n      state.policy=policy;el(\'receiptMarking\')');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
