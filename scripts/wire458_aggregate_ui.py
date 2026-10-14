import json
from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/pallet-composition.html");s=p.read_text(encoding="utf-8")
panel="""<section class="panel"><h2>Жизненный цикл агрегаций маркировки</h2>
<label>Склад<input id="agWare" type="number" min="1"></label>
<label>Исходный идентификатор паллеты<input id="agOrigin" maxlength="200" autocomplete="off"></label>
<button id="agRead">Открыть агрегации исходного состава</button>
<label>Причина<select id="agReason"><option value="OPENED">Упаковка вскрыта</option><option value="REPACKED">Переупаковка</option><option value="DAMAGED">Упаковка повреждена</option><option value="COMPOSITION_CHANGED">Состав изменён</option></select></label>
<label>Документ или основание<input id="agReference" maxlength="200"></label>
<p>Отмена запрещает использовать старый код и родительские агрегации. Остаток и уникальные коды единиц сохраняются. Государственное подтверждение оформляется отдельно.</p>
<table><thead><tr><th>Система / профиль</th><th>Уровень</th><th>Отпечаток кода</th><th>Состояние</th><th>Операция отмены</th><th>Действие</th></tr></thead><tbody id="agRows"></tbody></table>
<p id="agMessage" role="status"></p><pre id="agPending"></pre><button id="agRetry" hidden>Повторить сохранённую операцию</button></section>
"""
assert "agRows"not in s;s=s.replace("<p>Состояние остатков",panel+"<p>Состояние остатков")
s=s.replace('<script src="pallet-composition.js"></script>','<script src="pallet-composition.js"></script><script src="aggregate-lifecycle.js"></script>')
print(json.dumps({str(p):s}))
