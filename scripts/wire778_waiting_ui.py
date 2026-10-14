from pathlib import Path
import json
out={}
section="""<section class="panel"><h2>Перемещение отобранного товара в ожидание</h2>
<p>После переноса СТ на другой день создайте штатные задания на перемещение в настроенную ячейку ожидания. Количество и резерв под заказ сохраняются.</p>
<label>Решение о переносе СТ<input id="swDecision" maxlength="100" placeholder="Выберите решение из истории"></label>
<button id="swPlan">Создать задания ожидания</button><button id="swRetry" disabled>Повторить сохранённую команду</button>
<p id="swPending"></p><p id="swMessage"></p></section>
"""
for name in ("day-reconciliation.html",):
 p=Path("wiki-raw/wms_admin_ui_reference")/name;t=p.read_text(encoding="utf-8")
 anchor='<script src="st-deferral.js"></script>'
 assert anchor in t and 'st-waiting-tasks.js' not in t
 t=t.replace('</main>',section+'</main>').replace(anchor,anchor+'\n<script src="st-waiting-tasks.js"></script>')
 out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
anchor="   localStorage.removeItem(key());context=null;"
assert anchor in t
t=t.replace(anchor,"   window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:result}));\n"+anchor)
anchor="tr.appendChild(td);}return tr;"
assert anchor in t
t=t.replace(anchor,"""tr.appendChild(td);}
     const action=document.createElement('td'),button=document.createElement('button');
     button.textContent='Задания ожидания';
     button.addEventListener('click',()=>window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:row})));
     action.appendChild(button);tr.appendChild(action);return tr;""")
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
