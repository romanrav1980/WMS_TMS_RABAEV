import json
from pathlib import Path
out={}
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
anchor='<section class="panel" data-permission="transport_dispatch_view"><h2>СТ выбранной даты'
assert anchor in s
section="""<section class="panel" data-permission="transport_dispatch_view"><h2>Совместный осмотр грузовой зоны</h2>
<p>Начальник склада и диспетчер подписывают результат осмотра разными учётными записями. Подписи относятся к сохранённому снимку сверки и не закрывают день или внешние обязательства.</p>
<label>Операция сохранённой сверки<input id="diReview" maxlength="100"></label><button id="diRead">Прочитать подписи</button>
<label>Роль<select id="diRole"><option value="WAREHOUSE_CHIEF">Начальник склада</option><option value="DISPATCHER">Диспетчер</option></select></label>
<label>Результат физического осмотра<select id="diObserved"><option value="">Выберите результат</option><option value="EMPTY">Зона пуста</option><option value="NON_EMPTY">Зона не пуста</option></select></label>
<label>Осмотренные ворота/линии и основание<textarea id="diNote" maxlength="500"></textarea></label>
<button id="diSave" disabled>Подписать осмотр</button><button id="diRetry" disabled>Повторить сохранённую подпись</button><button id="diResolve" disabled>Проверить исход подписи</button>
<p id="diPending"></p><p id="diMessage" role="status"></p><div id="diRows"></div></section>
"""+anchor
s=s.replace(anchor,section).replace('<script src="day-review-history.js"></script>','<script src="day-review-history.js"></script><script src="day-inspection.js"></script>')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-review-history.js");s=p.read_text(encoding="utf-8")
anchor="paragraph('Запись сверки сохраняет открытые обязательства. Закрытие дня и внешнее подтверждение не объявлены.'));"
assert anchor in s
s=s.replace(anchor,anchor+'\n   window.dispatchEvent(new CustomEvent("wms-day-review-selected",{detail:{operation_id:op}}));')
out[str(p)]=s
print(json.dumps(out))
